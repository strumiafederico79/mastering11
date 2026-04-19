import uuid
import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.models import JobCreateResponse, JobStatusResponse
from app.core.paths import UPLOAD_DIR
from app.services.job_store import read_job, write_job
from app.services.learning import get_learning_stats
from app.services.plugin_scan import scan_plugins
from app.services.utils import slugify_filename
from app.worker_app import celery_app

app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)

@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": settings.app_name}

@app.get("/api/plugins")
def plugins():
    return scan_plugins()

@app.get("/api/learning")
def learning():
    return get_learning_stats()

@app.post("/api/jobs", response_model=JobCreateResponse)
async def create_job(
    file: UploadFile = File(...),
    mode: str = Form("human_master"),
    options_json: str = Form("{}"),
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Archivo inválido.")
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Archivo excede {settings.max_upload_mb} MB.")

    safe_name = slugify_filename(file.filename)
    input_filename = f"{uuid.uuid4().hex}_{safe_name}"
    input_path = UPLOAD_DIR / input_filename
    input_path.write_bytes(raw)

    job_id = uuid.uuid4().hex
    try:
        options = json.loads(options_json or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="options_json inválido.") from exc

    task = celery_app.send_task("app.tasks.run_mastering", args=[job_id, input_filename, mode, options])

    write_job(job_id, {
        "job_id": job_id,
        "task_id": task.id,
        "status": "queued",
        "progress": 0,
        "message": "En cola...",
        "mode": mode,
        "options": options,
        "profile": None,
        "analysis": {},
        "decision": {},
        "chain": {},
        "metrics": {},
        "outputs": {},
        "issues": [],
        "error": None,
    })
    return JobCreateResponse(job_id=job_id, task_id=task.id, status="queued")

@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str):
    try:
        payload = read_job(job_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Job no encontrado.") from exc
    return JobStatusResponse(**payload)

@app.get("/api/jobs/{job_id}/download")
def download_job_output(job_id: str, fmt: str = Query("wav", pattern="^(wav|mp3)$")):
    try:
        payload = read_job(job_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Job no encontrado.") from exc
    if payload.get("status") != "done":
        raise HTTPException(status_code=409, detail="El job aún no terminó.")
    path_key = "wav_path" if fmt == "wav" else "mp3_path"
    file_path = payload.get("outputs", {}).get(path_key)
    if not file_path:
        raise HTTPException(status_code=404, detail="Salida no disponible.")
    p = Path(file_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Archivo exportado no encontrado.")
    media_type = "audio/wav" if fmt == "wav" else "audio/mpeg"
    return FileResponse(p, media_type=media_type, filename=p.name)

frontend_dir = Path("/app/frontend")
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

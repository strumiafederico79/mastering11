import traceback, subprocess

from app.worker_app import celery_app
from app.core.paths import UPLOAD_DIR, OUTPUT_DIR
from app.core.config import settings
from app.services.audio_io import load_audio_for_analysis
from app.services.analyzer import analyze_audio
from app.services.decision_engine import decide_mastering
from app.services.mastering_chain import build_ffmpeg_filter_chain
from app.services.ffmpeg_tools import export_mp3, loudnorm_two_pass
from app.services.job_store import read_job, write_job
from app.services.learning import append_learning

def update_job(job_id: str, **fields):
    try:
        payload = read_job(job_id)
    except FileNotFoundError:
        payload = {"job_id": job_id}
    payload.update(fields)
    write_job(job_id, payload)

@celery_app.task(name="app.tasks.run_mastering")
def run_mastering(job_id: str, input_filename: str, mode: str = "human_master", options: dict | None = None):
    input_path = UPLOAD_DIR / input_filename
    stage1_wav = OUTPUT_DIR / f"{job_id}_stage1.wav"
    final_wav = OUTPUT_DIR / f"{job_id}.wav"
    final_mp3 = OUTPUT_DIR / f"{job_id}.mp3"

    try:
        update_job(job_id, status="processing", progress=5, message="Cargando audio...")
        if not input_path.exists():
            raise FileNotFoundError(f"No existe el archivo de entrada: {input_path}")

        print(f"[{job_id}] ANALYSIS LOAD {input_path}", flush=True)
        y, sr = load_audio_for_analysis(str(input_path), settings.target_sr, settings.analysis_max_seconds)

        update_job(job_id, progress=15, message="Analizando audio...")
        print(f"[{job_id}] ANALYZING", flush=True)
        analysis = analyze_audio(y, sr)

        update_job(job_id, progress=30, message="Tomando decisiones...", analysis=analysis, issues=analysis.get("issues", []))
        decision = decide_mastering(analysis, mode=mode, options=options)

        update_job(job_id, progress=45, message="Procesando cadena de mastering...", decision=decision)
        af_chain, actions = build_ffmpeg_filter_chain(decision)

        cmd_stage1 = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-af", af_chain,
            "-ar", str(settings.target_sr),
            "-ac", "2",
            str(stage1_wav),
        ]
        print(f"[{job_id}] STAGE1 FFMPEG", flush=True)
        subprocess.run(cmd_stage1, check=True, capture_output=True, text=True)

        update_job(job_id, progress=75, message="Normalizando loudness...", chain={"stages": [a["stage"] for a in actions], "actions": actions})
        metrics = loudnorm_two_pass(str(stage1_wav), str(final_wav), decision["target_lufs"], decision["limiter_ceiling_dbtp"], 11.0)

        update_job(job_id, progress=90, message="Exportando MP3...", metrics=metrics)
        export_mp3(str(final_wav), str(final_mp3))

        append_learning({
            "genre": decision.get("genre", "general"),
            "target_lufs": decision.get("target_lufs", -10.5),
            "issues": analysis.get("issues", []),
        })

        update_job(
            job_id,
            status="done",
            progress=100,
            message="Mastering terminado.",
            profile=decision.get("preset_name", "Human Master"),
            outputs={"wav_path": str(final_wav), "mp3_path": str(final_mp3)},
            error=None,
        )
        print(f"[{job_id}] DONE", flush=True)
        return {"ok": True, "job_id": job_id}

    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
        update_job(job_id, status="error", progress=100, message="Error en mastering.", error=err)
        print(f"[{job_id}] ERROR\n{err}", flush=True)
        raise

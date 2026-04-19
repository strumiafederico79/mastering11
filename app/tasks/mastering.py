import traceback, subprocess

from app.worker_app import celery_app
from app.core.paths import UPLOAD_DIR, OUTPUT_DIR
from app.core.config import settings
from app.services.audio_io import load_audio_for_analysis
from app.services.analyzer import analyze_audio
from app.services.decision_engine import decide_mastering
from app.services.mastering_chain import build_ffmpeg_filter_chain, build_safe_filter_chain
from app.services.ffmpeg_tools import export_mp3, loudnorm_two_pass
from app.services.job_store import read_job, write_job
from app.services.learning import append_learning

def _normalize_af_chain(af_chain: str) -> str:
    """
    Normalize known-incompatible filter params that may still appear in old jobs
    or stale worker deployments.
    """
    normalized = af_chain.replace(":level=disabled", "")
    # Clean accidental duplicate separators.
    normalized = ",".join([chunk for chunk in normalized.split(",") if chunk])
    return normalized

def _run_stage1_ffmpeg(cmd_stage1: list[str], af_chain: str) -> None:
    try:
        subprocess.run(cmd_stage1, check=True, capture_output=True, text=True)
        return
    except subprocess.CalledProcessError as ff_err:
        stderr_text = (ff_err.stderr or "").strip()
        stdout_text = (ff_err.stdout or "").strip()

    normalized_chain = _normalize_af_chain(af_chain)
    if normalized_chain != af_chain:
        retry_cmd = cmd_stage1.copy()
        retry_cmd[retry_cmd.index("-af") + 1] = normalized_chain
        try:
            subprocess.run(retry_cmd, check=True, capture_output=True, text=True)
            return
        except subprocess.CalledProcessError as retry_err:
            stderr_text = ((retry_err.stderr or "").strip() or stderr_text)
            stdout_text = ((retry_err.stdout or "").strip() or stdout_text)
            ff_err = retry_err

    debug_tail = (stderr_text or stdout_text)[-3000:]
    raise RuntimeError(
        f"Falló ffmpeg en etapa 1 (exit={ff_err.returncode}). "
        f"Detalle: {debug_tail or 'sin salida de diagnóstico'}"
    ) from ff_err

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
        try:
            subprocess.run(cmd_stage1, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as ff_err:
            fallback_chain = build_safe_filter_chain()
            update_job(
                job_id,
                progress=55,
                message="Compatibilidad ffmpeg: reintentando con cadena segura...",
                chain={
                    "stages": [a["stage"] for a in actions] + ["safe_fallback"],
                    "actions": actions + [{"stage": "safe_fallback", "reason": "ffmpeg_filter_compatibility"}],
                    "ffmpeg_error": (ff_err.stderr or ff_err.stdout or str(ff_err))[:1400],
                },
            )
            fallback_cmd = [
                "ffmpeg", "-y", "-i", str(input_path),
                "-af", fallback_chain,
                "-ar", str(settings.target_sr),
                "-ac", "2",
                str(stage1_wav),
            ]
            subprocess.run(fallback_cmd, check=True, capture_output=True, text=True)

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

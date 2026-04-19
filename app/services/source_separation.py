from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def separate_with_demucs(input_audio: str, out_root: str) -> dict[str, str] | None:
    """
    Runs Demucs 4-stem separation when available.
    Returns paths for vocals/drums/bass/other if successful, else None.
    """
    demucs_bin = shutil.which("demucs")
    if not demucs_bin:
        return None

    out_dir = Path(out_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        demucs_bin,
        "-n", "htdemucs",
        "-o", str(out_dir),
        input_audio,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    track_name = Path(input_audio).stem
    stem_dir = out_dir / "htdemucs" / track_name
    vocals = stem_dir / "vocals.wav"
    drums = stem_dir / "drums.wav"
    bass = stem_dir / "bass.wav"
    other = stem_dir / "other.wav"
    if not (vocals.exists() and drums.exists() and bass.exists() and other.exists()):
        return None

    return {
        "vocals_wav_path": str(vocals),
        "drums_wav_path": str(drums),
        "bass_wav_path": str(bass),
        "other_wav_path": str(other),
    }

import json, subprocess

def export_mp3(in_wav: str, out_mp3: str) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-i", in_wav, "-codec:a", "libmp3lame", "-b:a", "320k", out_mp3],
        check=True, capture_output=True, text=True,
    )

def export_stem(in_wav: str, out_wav: str, stem_mode: str) -> None:
    if stem_mode == "acapella":
        af = "pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1"
    elif stem_mode == "instrumental":
        af = "pan=stereo|c0=c0-c1|c1=c1-c0"
    else:
        raise ValueError(f"stem_mode inválido: {stem_mode}")

    subprocess.run(
        ["ffmpeg", "-y", "-i", in_wav, "-af", af, "-ar", "44100", "-ac", "2", out_wav],
        check=True, capture_output=True, text=True,
    )

def loudnorm_two_pass(in_wav: str, out_wav: str, target_lufs: float, true_peak: float = -1.0, lra: float = 11.0) -> dict:
    cmd1 = [
        "ffmpeg", "-y", "-i", in_wav,
        "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:print_format=json",
        "-f", "null", "-"
    ]
    res1 = subprocess.run(cmd1, capture_output=True, text=True, check=True)
    stderr = res1.stderr
    start = stderr.rfind("{")
    end = stderr.rfind("}")
    metrics = {}
    if start != -1 and end != -1 and end > start:
        metrics = json.loads(stderr[start:end+1])

    measured_i = metrics.get("input_i", "-18.0")
    measured_tp = metrics.get("input_tp", "-2.0")
    measured_lra = metrics.get("input_lra", "7.0")
    measured_thresh = metrics.get("input_thresh", "-28.0")
    offset = metrics.get("target_offset", "0.0")

    af2 = (
        f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:"
        f"measured_I={measured_i}:measured_TP={measured_tp}:"
        f"measured_LRA={measured_lra}:measured_thresh={measured_thresh}:"
        f"offset={offset}:linear=true:print_format=json"
    )
    subprocess.run(["ffmpeg", "-y", "-i", in_wav, "-af", af2, out_wav], capture_output=True, text=True, check=True)
    return metrics

def apply_dither(in_wav: str, out_wav: str, profile: str = "triangular_hp") -> None:
    if profile == "triangular_hp":
        af = "aresample=44100:dither_method=triangular_hp"
    else:
        af = "aresample=44100:dither_method=triangular"
    subprocess.run(
        ["ffmpeg", "-y", "-i", in_wav, "-af", af, "-c:a", "pcm_s16le", out_wav],
        check=True, capture_output=True, text=True,
    )

def mix_stems_to_instrumental(drums_wav: str, bass_wav: str, other_wav: str, out_wav: str) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", drums_wav,
            "-i", bass_wav,
            "-i", other_wav,
            "-filter_complex", "amix=inputs=3:normalize=0",
            "-ar", "44100",
            "-ac", "2",
            out_wav,
        ],
        check=True, capture_output=True, text=True,
    )

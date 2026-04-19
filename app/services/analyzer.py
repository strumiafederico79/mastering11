import numpy as np
import librosa

def analyze_audio(y, sr):
    max_seconds = 60
    max_samples = sr * max_seconds
    if len(y) > max_samples:
        y = y[:max_samples]

    spec = np.abs(librosa.stft(y, n_fft=1024, hop_length=1024))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=1024)

    def band(f1, f2):
        idx = (freqs >= f1) & (freqs < f2)
        if not np.any(idx):
            return 0.0
        return float(np.mean(spec[idx]))

    low = band(20, 120)
    low_mid = band(120, 500)
    mid = band(500, 4000)
    high = band(4000, 10000)
    air = band(10000, 20000)

    peak = float(np.max(np.abs(y)))
    rms = float(np.mean(np.abs(y)))
    crest = float(peak / (rms + 1e-6))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_mean = float(np.mean(onset_env))

    y_harm, y_perc = librosa.effects.hpss(y)
    harm_rms = float(np.sqrt(np.mean(np.square(y_harm))) + 1e-8)
    perc_rms = float(np.sqrt(np.mean(np.square(y_perc))) + 1e-8)
    harmonic_ratio = float(harm_rms / max(perc_rms, 1e-8))

    vocal_band = band(250, 3500)
    vocal_presence = float(vocal_band / max(mid + low_mid, 1e-6))
    chorus_density = float(min(1.0, (harmonic_ratio * 0.28) + (vocal_presence * 0.65)))
    if vocal_presence > 0.34 and harmonic_ratio > 1.25:
        arrangement_focus = "vocal_led"
    elif harmonic_ratio < 0.8 and onset_mean > 0.9:
        arrangement_focus = "instrumental_driven"
    else:
        arrangement_focus = "balanced_mix"

    issues = []
    if low_mid > max(mid * 2.6, 0.1):
        issues.append("mud")
    if air < max(high * 0.20, 0.05):
        issues.append("lack_of_air")
    if high > max(mid * 1.5, 0.3):
        issues.append("harsh")
    if crest < 4.8:
        issues.append("weak_transients")
    if low > max(mid * 4.0, 0.2):
        issues.append("loose_low_end")
    if vocal_presence > 0.42 and low_mid > max(mid * 2.4, 0.1):
        issues.append("vocal_masking")
    if chorus_density > 0.70 and high > max(mid * 1.2, 0.22):
        issues.append("chorus_harshness")

    arrangement_tags = []
    if arrangement_focus == "vocal_led":
        arrangement_tags.append("voz_principal_fuerte")
    if chorus_density > 0.66:
        arrangement_tags.append("coros_presentes")
    if harmonic_ratio < 0.9:
        arrangement_tags.append("instrumental_dominante")
    if onset_mean < 0.55:
        arrangement_tags.append("ataque_suave")

    n_sections = 6
    section_len = max(1, len(y) // n_sections)
    section_rms_db = []
    section_peak_db = []
    for i in range(n_sections):
        start = i * section_len
        end = len(y) if i == (n_sections - 1) else (i + 1) * section_len
        chunk = y[start:end]
        if len(chunk) == 0:
            section_rms_db.append(-80.0)
            continue
        chunk_rms = float(np.sqrt(np.mean(np.square(chunk))) + 1e-8)
        section_rms_db.append(float(20 * np.log10(chunk_rms + 1e-8)))
        chunk_peak = float(np.max(np.abs(chunk)) + 1e-8)
        section_peak_db.append(float(20 * np.log10(chunk_peak)))

    macro_dynamics = float(np.max(section_rms_db) - np.min(section_rms_db))
    hook_lift_db = float(np.mean(section_rms_db[-2:]) - np.mean(section_rms_db[:2]))
    clipping_sections = [idx for idx, p in enumerate(section_peak_db) if p > -0.2]
    true_peak_est_db = float(20 * np.log10(peak + 1e-8))
    sibilance_band = band(5000, 10000)
    sibilance_index = float(sibilance_band / max(mid, 1e-6))
    harshness_index = float(high / max(mid, 1e-6))
    resonance_idx = (freqs >= 1000) & (freqs <= 9000)
    resonance_hz = 3500
    if np.any(resonance_idx):
        idx = np.where(resonance_idx)[0]
        sub_spec = np.mean(spec[idx], axis=1)
        peak_i = int(np.argmax(sub_spec))
        resonance_hz = int(freqs[idx][peak_i])
    ab_match_gain_db = float(-18.0 - (20 * np.log10(rms + 1e-8)))
    loudness_radar = [float(x) for x in section_rms_db]
    bass_idx = (freqs >= 40) & (freqs <= 160)
    bass_note_hz = 80.0
    if np.any(bass_idx):
        idx = np.where(bass_idx)[0]
        bass_spec = np.mean(spec[idx], axis=1)
        bass_note_hz = float(freqs[idx][int(np.argmax(bass_spec))])
    if hook_lift_db > 1.3:
        arrangement_tags.append("hook_con_lift")
    if macro_dynamics > 5.0:
        arrangement_tags.append("macro_dinamica_amplia")

    return {
        "low": low,
        "low_mid": low_mid,
        "mid": mid,
        "high": high,
        "air": air,
        "peak": peak,
        "rms": rms,
        "crest": crest,
        "centroid": centroid,
        "rolloff": rolloff,
        "flatness": flatness,
        "tempo": float(tempo),
        "onset_mean": onset_mean,
        "harmonic_ratio": harmonic_ratio,
        "vocal_presence": vocal_presence,
        "chorus_density": chorus_density,
        "arrangement_focus": arrangement_focus,
        "arrangement_tags": arrangement_tags,
        "section_rms_db": section_rms_db,
        "macro_dynamics_db": macro_dynamics,
        "hook_lift_db": hook_lift_db,
        "section_peak_db": section_peak_db,
        "clipping_sections": clipping_sections,
        "true_peak_est_db": true_peak_est_db,
        "sibilance_index": sibilance_index,
        "harshness_index": harshness_index,
        "resonance_hz": resonance_hz,
        "ab_match_gain_db": ab_match_gain_db,
        "loudness_radar": loudness_radar,
        "bass_note_hz": bass_note_hz,
        "phase_corr": 1.0,
        "stereo_width": 0.0,
        "issues": issues,
    }

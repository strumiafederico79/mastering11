import librosa
import soundfile as sf

def load_audio_for_analysis(path: str, sr: int, max_seconds: int):
    y, sr = librosa.load(path, sr=sr, mono=True)
    max_samples = sr * max_seconds
    if len(y) > max_samples:
        y = y[:max_samples]
    return y.astype("float32", copy=False), sr

def save_wav(path: str, y, sr: int):
    sf.write(path, y, sr, subtype="PCM_24")

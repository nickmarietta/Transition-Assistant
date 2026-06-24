import io

import numpy as np
import librosa

from typing import Optional

# Krumhansl-Schmuckler key profiles
_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def _detect_key(y: np.ndarray, sr: int) -> tuple:
    """Return (spotify_key 0-11, mode 0=minor/1=major) via chroma + key profiles."""
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    mean_chroma = chroma.mean(axis=1)

    best_score = -np.inf
    best_key = 0
    best_mode = 1

    for i in range(12):
        rotated = np.roll(mean_chroma, -i)
        major_r = float(np.corrcoef(rotated, _MAJOR)[0, 1])
        minor_r = float(np.corrcoef(rotated, _MINOR)[0, 1])
        if major_r > best_score:
            best_score, best_key, best_mode = major_r, i, 1
        if minor_r > best_score:
            best_score, best_key, best_mode = minor_r, i, 0

    return best_key, best_mode


def analyze_audio(audio_bytes: bytes, duration: float = 60.0) -> dict:
    """Analyze the first `duration` seconds of an audio file.

    Returns bpm, key (Spotify 0-11), mode (0=minor/1=major), energy (0-1),
    and an empty segments list reserved for future structural labeling.
    """
    y, sr = librosa.load(io.BytesIO(audio_bytes), duration=duration, mono=True)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(np.atleast_1d(tempo)[0])

    key, mode = _detect_key(y, sr)

    rms_mean = float(np.mean(librosa.feature.rms(y=y)))
    # Scale: ~0.02 rms = quiet, ~0.15+ rms = high energy; clip to [0, 1]
    energy = float(np.clip(rms_mean / 0.15, 0.0, 1.0))

    return {
        "bpm": round(bpm, 1),
        "key": key,
        "mode": mode,
        "energy": round(energy, 3),
        # Structured for a future labeling pipeline — each segment will carry
        # {start, end, label, energy} once structural detection is added.
        "segments": [],
    }

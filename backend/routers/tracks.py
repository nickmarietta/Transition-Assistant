import librosa
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from scoring import CAMELOT
from services.audio import analyze_audio

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/health")
def tracks_health():
    """Verify librosa (and numpy) are installed and importable."""
    return {
        "status": "ok",
        "librosa": librosa.__version__,
        "numpy": np.__version__,
    }


@router.post("/analyze")
async def analyze_track(file: UploadFile = File(...)):
    """Accept an audio file upload and return BPM, key, mode, energy, and camelot."""
    print(f"[tracks/analyze] file={file.filename!r}  content_type={file.content_type!r}")

    audio_bytes = await file.read()
    print(f"[tracks/analyze] received {len(audio_bytes):,} bytes")

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        result = analyze_audio(audio_bytes)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Audio analysis failed: {exc}")

    result["camelot"] = CAMELOT.get((result["key"], result["mode"]))
    print(
        f"[tracks/analyze] → bpm={result['bpm']}  "
        f"key={result['key']}  mode={result['mode']}  "
        f"camelot={result['camelot']}  energy={result['energy']}"
    )
    return result

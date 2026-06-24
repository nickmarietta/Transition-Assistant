from fastapi import APIRouter, File, HTTPException, UploadFile

from scoring import CAMELOT
from services.audio import analyze_audio

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.post("/analyze")
async def analyze_track(file: UploadFile = File(...)):
    """Accept an audio file upload and return BPM, key, mode, energy, and camelot."""
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        result = analyze_audio(audio_bytes)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Audio analysis failed: {exc}")

    result["camelot"] = CAMELOT.get((result["key"], result["mode"]))
    return result

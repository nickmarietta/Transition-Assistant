from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from scoring import score_transition

router = APIRouter(prefix="/scoring", tags=["scoring"])


class TrackFeatures(BaseModel):
    id: str
    name: str
    artist: str
    key: int
    mode: int
    bpm: Optional[float]
    energy: Optional[float]
    camelot: Optional[str] = None


class SuggestRequest(BaseModel):
    current_track_id: str
    tracks: List[TrackFeatures]


@router.post("/suggest")
def suggest(req: SuggestRequest):
    current = next((t for t in req.tracks if t.id == req.current_track_id), None)
    if not current or current.bpm is None or current.energy is None:
        return {"suggestions": []}

    results = []
    for track in req.tracks:
        if track.id == req.current_track_id:
            continue
        if track.bpm is None or track.energy is None:
            continue
        scores = score_transition(
            {"key": current.key, "mode": current.mode, "bpm": current.bpm, "energy": current.energy},
            {"key": track.key, "mode": track.mode, "bpm": track.bpm, "energy": track.energy},
        )
        results.append({"track": track.model_dump(), **scores})

    results.sort(key=lambda x: x["score"], reverse=True)
    return {"suggestions": results}

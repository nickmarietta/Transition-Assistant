import re
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

from routers.auth import get_token
from services import spotify as spotify_svc
from scoring import CAMELOT

router = APIRouter(prefix="/playlist", tags=["playlist"])

# ---------------------------------------------------------------------------
# Demo dataset — covers every scoring case without requiring Spotify auth.
#
# All tracks built around "Solar Power" (9B, 122 BPM, 0.65 energy) as the
# Now Playing anchor, producing a full spread of scores when you select it:
#
#   Open Road    10B  124 BPM  0.68  →  94  (adjacent key, tight BPM, smooth energy)
#   Midnight Keys 8B  121 BPM  0.62  →  94  (adjacent key, tight BPM, smooth energy)
#   Shadow Walk   9A  122 BPM  0.58  →  90  (relative minor, tight BPM, smooth energy)
#   Quiet Storm   9B  120 BPM  0.25  →  88  (same key, tight BPM, ⚠ energy jump)
#   Golden Hour   8B  126 BPM  0.72  →  86  (adjacent key, within 5 BPM, smooth energy)
#   Crystal Night 3B  123 BPM  0.70  →  76  (bad key, perfect BPM, smooth energy)
#   Last Light    5B  128 BPM  0.75  →  56  (bad key, within 10 BPM, smooth energy)
#   Rush Hour    10B  145 BPM  0.95  →  54  (adjacent key, ⚠ BPM crash + energy jump)
#   Deep Current  4A  100 BPM  0.97  →  36  (bad key, BPM crash, ⚠ energy jump)
# ---------------------------------------------------------------------------
_DEMO_TRACKS = [
    {"id": "demo-1",  "name": "Solar Power",   "artist": "Lena Bay",    "duration_ms": 210000, "key": 7, "mode": 1, "bpm": 122.0, "energy": 0.65, "camelot": "9B"},
    {"id": "demo-2",  "name": "Open Road",      "artist": "Felix North", "duration_ms": 215000, "key": 2, "mode": 1, "bpm": 124.0, "energy": 0.68, "camelot": "10B"},
    {"id": "demo-3",  "name": "Midnight Keys",  "artist": "Clara V",     "duration_ms": 198000, "key": 0, "mode": 1, "bpm": 121.0, "energy": 0.62, "camelot": "8B"},
    {"id": "demo-4",  "name": "Shadow Walk",    "artist": "Lena Bay",    "duration_ms": 225000, "key": 7, "mode": 0, "bpm": 122.5, "energy": 0.58, "camelot": "9A"},
    {"id": "demo-5",  "name": "Quiet Storm",    "artist": "Moss",        "duration_ms": 240000, "key": 7, "mode": 1, "bpm": 120.0, "energy": 0.25, "camelot": "9B"},
    {"id": "demo-6",  "name": "Rush Hour",      "artist": "Felix North", "duration_ms": 185000, "key": 2, "mode": 1, "bpm": 145.0, "energy": 0.95, "camelot": "10B"},
    {"id": "demo-7",  "name": "Crystal Night",  "artist": "Clara V",     "duration_ms": 200000, "key": 1, "mode": 1, "bpm": 123.0, "energy": 0.70, "camelot": "3B"},
    {"id": "demo-8",  "name": "Deep Current",   "artist": "Moss",        "duration_ms": 360000, "key": 5, "mode": 0, "bpm": 100.0, "energy": 0.97, "camelot": "4A"},
    {"id": "demo-9",  "name": "Golden Hour",    "artist": "Lena Bay",    "duration_ms": 230000, "key": 0, "mode": 1, "bpm": 126.0, "energy": 0.72, "camelot": "8B"},
    {"id": "demo-10", "name": "Last Light",     "artist": "Felix North", "duration_ms": 195000, "key": 3, "mode": 1, "bpm": 128.0, "energy": 0.75, "camelot": "5B"},
]


@router.get("/demo")
def get_demo_playlist():
    """Pre-seeded playlist for testing — no Spotify auth required."""
    return {
        "id": "demo",
        "name": "Demo Set",
        "track_count": len(_DEMO_TRACKS),
        "tracks": _DEMO_TRACKS,
    }


def _extract_playlist_id(url: str) -> str:
    match = re.search(r"playlist[/:]([A-Za-z0-9]+)", url)
    if not match:
        raise HTTPException(status_code=400, detail="Could not parse a playlist ID from that URL")
    return match.group(1)



@router.get("")
async def get_playlist(
    url: str,
    session_id: Optional[str] = Query(default=None),
):
    token = get_token(session_id)
    playlist_id = _extract_playlist_id(url)

    try:
        info, raw_tracks = await spotify_svc.get_playlist(playlist_id, token)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Spotify error ({exc.response.status_code}): {exc.response.text[:400]}",
        )

    if not raw_tracks:
        raise HTTPException(
            status_code=403,
            detail=(
                "No tracks could be loaded. Spotify's API only allows reading tracks "
                "from playlists you own. Make sure you're loading one of your own playlists."
            ),
        )

    try:
        track_ids = [t["id"] for t in raw_tracks]
        audio_features = await spotify_svc.get_audio_features(track_ids, token)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Audio features error ({exc.response.status_code}): {exc.response.text[:400]}",
        )

    tracks = []
    for track in raw_tracks:
        tid = track["id"]
        af = audio_features.get(tid) or {}
        key = af.get("key", -1)
        mode = af.get("mode", 1)

        tracks.append({
            "id": tid,
            "name": track["name"],
            "artist": ", ".join(a["name"] for a in track.get("artists", [])),
            "duration_ms": track.get("duration_ms"),
            "key": key,
            "mode": mode,
            "bpm": af.get("tempo"),
            "energy": af.get("energy"),
            "camelot": CAMELOT.get((key, mode)) if key != -1 else None,
        })

    return {
        "id": info["id"],
        "name": info["name"],
        "track_count": info["tracks"]["total"],
        "tracks": tracks,
    }

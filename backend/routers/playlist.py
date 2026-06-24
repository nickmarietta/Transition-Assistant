import re
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

from routers.auth import get_token
from services import spotify as spotify_svc
from scoring import CAMELOT

router = APIRouter(prefix="/playlist", tags=["playlist"])


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

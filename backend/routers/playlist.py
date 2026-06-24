import re
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

from routers.auth import get_token
from services import spotify as spotify_svc
from services.spotify import SPOTIFY_API
from scoring import CAMELOT

router = APIRouter(prefix="/playlist", tags=["playlist"])


def _extract_playlist_id(url: str) -> str:
    match = re.search(r"playlist[/:]([A-Za-z0-9]+)", url)
    if not match:
        raise HTTPException(status_code=400, detail="Could not parse a playlist ID from that URL")
    return match.group(1)


@router.get("/debug")
async def debug_playlist(
    url: str,
    session_id: Optional[str] = Query(default=None),
):
    """Returns raw Spotify responses both with and without a fields filter."""
    token = get_token(session_id)
    playlist_id = _extract_playlist_id(url)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        # Test 1: no fields filter — get everything Spotify returns
        plain = await client.get(
            f"{SPOTIFY_API}/playlists/{playlist_id}",
            headers=headers,
        )
        plain_data = plain.json()
        tracks_obj = plain_data.get("tracks") or {}

        # Test 2: with fields filter
        fields = "id,name,tracks.total,tracks.next,tracks.items(track(id,name,artists,duration_ms))"
        filtered = await client.get(
            f"{SPOTIFY_API}/playlists/{playlist_id}?fields={fields}",
            headers=headers,
        )
        filtered_data = filtered.json()

        top_items = plain_data.get("items")
        return {
            "plain": {
                "status": plain.status_code,
                "top_level_keys": list(plain_data.keys()),
                "tracks_present": "tracks" in plain_data,
                "top_items_type": type(top_items).__name__,
                "top_items_count": len(top_items) if isinstance(top_items, list) else None,
                "top_items_first": top_items[0] if isinstance(top_items, list) and top_items else None,
            },
            "with_fields": {
                "status": filtered.status_code,
                "url": str(filtered.url),
                "top_level_keys": list(filtered_data.keys()),
                "tracks_present": "tracks" in filtered_data,
                "body": filtered_data,
            },
        }


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

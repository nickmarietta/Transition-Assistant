from typing import Optional

import httpx

SPOTIFY_API = "https://api.spotify.com/v1"
SPOTIFY_AUTH = "https://accounts.spotify.com"


async def exchange_code(
    code: str, redirect_uri: str, client_id: str, client_secret: str
) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SPOTIFY_AUTH}/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            auth=(client_id, client_secret),
        )
        resp.raise_for_status()
        return resp.json()


async def get_playlist_info(playlist_id: str, access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SPOTIFY_API}/playlists/{playlist_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"fields": "id,name,description,images,tracks(total)"},
        )
        resp.raise_for_status()
        return resp.json()


async def get_playlist_tracks(playlist_id: str, access_token: str) -> list[dict]:
    tracks: list[dict] = []
    url = f"{SPOTIFY_API}/playlists/{playlist_id}/tracks"  # type: Optional[str]
    params: dict = {
        "fields": "items(track(id,name,artists,duration_ms)),next",
        "limit": 100,
    }

    async with httpx.AsyncClient() as client:
        while url:
            resp = await client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("items", []):
                track = item.get("track")
                if track and track.get("id"):
                    tracks.append(track)

            url = data.get("next")
            params = {}  # next URL already carries query params

    return tracks


async def get_audio_features(track_ids: list[str], access_token: str) -> dict[str, dict]:
    """Returns audio features keyed by track id.

    Returns an empty dict silently if Spotify returns 403/404 — the
    audio-features endpoint is deprecated for apps created after Nov 2024.
    """
    features: dict[str, dict] = {}

    async with httpx.AsyncClient() as client:
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i : i + 100]
            resp = await client.get(
                f"{SPOTIFY_API}/audio-features",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"ids": ",".join(batch)},
            )
            if resp.status_code in (403, 404):
                # Endpoint not available for this app — skip gracefully
                break
            resp.raise_for_status()
            for af in resp.json().get("audio_features") or []:
                if af and af.get("id"):
                    features[af["id"]] = af

    return features

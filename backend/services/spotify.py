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


async def get_playlist(playlist_id: str, access_token: str) -> tuple:
    """Fetch playlist metadata and all tracks using only the /playlists/{id} endpoint.

    The /playlists/{id}/tracks sub-endpoint is restricted for newer Spotify apps,
    but track data is available through the main playlist endpoint's tracks field.
    Handles pagination by following the tracks.next cursor.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    tracks = []

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SPOTIFY_API}/playlists/{playlist_id}",
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

        # Newer Spotify apps: paging object is at data["items"], not data["tracks"].
        # Within each playlist item, the track is keyed as "item" not "track".
        tracks_obj = data.get("tracks") or data.get("items") or {}
        raw_items = tracks_obj.get("items") or []
        total = tracks_obj.get("total", 0)
        next_url = tracks_obj.get("next")

        info = {
            "id": data.get("id", playlist_id),
            "name": data.get("name", "Unknown Playlist"),
            "tracks": {"total": total},
        }

        for item in raw_items:
            # New apps use "item" key; old format used "track"
            track = (item.get("item") or item.get("track")) if item else None
            if track and track.get("id"):
                tracks.append(track)

        offset = len(tracks)
        while next_url:
            page_resp = await client.get(
                f"{SPOTIFY_API}/playlists/{playlist_id}/tracks?offset={offset}&limit=100",
                headers=headers,
            )
            if page_resp.status_code == 403:
                break
            page_resp.raise_for_status()
            page = page_resp.json()
            for item in page.get("items") or []:
                track = (item.get("item") or item.get("track")) if item else None
                if track and track.get("id"):
                    tracks.append(track)
            next_url = page.get("next")
            offset = len(tracks)

    return info, tracks


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

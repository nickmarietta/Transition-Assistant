import os
import secrets
import time
import uuid
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from services.spotify import exchange_code

SPOTIFY_API = "https://api.spotify.com/v1"

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory stores (v1 — no persistence)
_sessions: dict = {}      # session_id → {access_token, refresh_token, expires_at}
_state_store: dict = {}   # CSRF state → issued_at timestamp

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/auth/callback")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://127.0.0.1:3000")

SCOPES = "playlist-read-private playlist-read-collaborative"


def get_token(session_id: Optional[str]) -> str:
    """Return a valid access token for the given session or raise 401."""
    if not session_id or session_id not in _sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    data = _sessions[session_id]
    if data.get("expires_at", 0) < time.time():
        _sessions.pop(session_id, None)
        raise HTTPException(status_code=401, detail="Session expired — please log in again")
    return data["access_token"]


@router.get("/login")
def login():
    state = secrets.token_urlsafe(16)
    _state_store[state] = time.time()
    params = urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": state,
    })
    return RedirectResponse(f"https://accounts.spotify.com/authorize?{params}")


@router.get("/callback")
async def callback(code: str, state: str):
    issued_at = _state_store.pop(state, None)
    if issued_at is None or time.time() - issued_at > 600:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    token_data = await exchange_code(code, REDIRECT_URI, CLIENT_ID, CLIENT_SECRET)

    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token"),
        "expires_at": time.time() + token_data.get("expires_in", 3600),
    }

    # Pass session_id to the frontend via URL param — avoids all SameSite cookie issues
    return RedirectResponse(f"{FRONTEND_URL}?session_id={session_id}")


@router.get("/status")
def status(session_id: Optional[str] = Query(default=None)):
    logged_in = (
        session_id is not None
        and session_id in _sessions
        and _sessions[session_id].get("expires_at", 0) > time.time()
    )
    return {"logged_in": logged_in}


@router.get("/me")
async def me(session_id: Optional[str] = Query(default=None)):
    """Returns the Spotify profile for the logged-in user."""
    token = get_token(session_id)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SPOTIFY_API}/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    if not resp.is_success:
        raise HTTPException(status_code=resp.status_code, detail="Failed to fetch Spotify profile")
    data = resp.json()
    images = data.get("images") or []
    return {
        "id": data.get("id"),
        "display_name": data.get("display_name") or data.get("id"),
        "email": data.get("email"),
        "image_url": images[0]["url"] if images else None,
    }


@router.post("/logout")
def logout_user(session_id: Optional[str] = Query(default=None)):
    if session_id:
        _sessions.pop(session_id, None)
    return {"ok": True}

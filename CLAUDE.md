# DJ Transition Assistant

## What this is
A web app that helps a DJ find the best next track from a Spotify playlist in real time.
The user pastes a Spotify playlist URL, the app fetches all tracks, scores compatibility
between every pair, and presents a ranked "what plays next" view during a live set.

## Stack
- Frontend: Next.js 14 App Router, TypeScript, Tailwind CSS
- Backend: FastAPI (Python), runs on localhost:8000
- Audio analysis: librosa (for uploaded MP3s)
- No database in v1 — all state is in-memory / client-side

## Repo structure
/frontend   → Next.js app
/backend    → FastAPI app

## Core scoring logic (must implement exactly)
Compatibility score = (0.4 * key_score) + (0.4 * bpm_score) + (0.2 * energy_score)

Key score: based on Camelot Wheel proximity
- Same key = 100
- Adjacent (±1) = 85
- Relative major/minor = 75
- All else = 40

BPM score:
- Within 2 BPM = 100
- Within 5 BPM = 80
- Within 10 BPM = 60
- Beyond 10 = 30

Energy score (from Spotify energy field, 0.0–1.0):
- Delta < 0.1 = 100
- Delta < 0.2 = 80
- Delta < 0.3 = 60
- Delta >= 0.3 = 40 (flag as "energy jump" in UI, don't block)

## Spotify API
- Use Authorization Code Flow for OAuth
- Scopes needed: playlist-read-private, playlist-read-collaborative
- Audio features endpoint: GET /audio-features (batch, up to 100 track IDs per call)
- Store access token in memory only (no persistence in v1)

## What NOT to build in v1
- No user accounts
- No database
- No set export back to Spotify
- No LLM layer
- No FX suggestions
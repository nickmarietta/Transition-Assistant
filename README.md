# DJ Transition Assistant

A web app that helps a DJ find the best next track from a Spotify playlist in real time. Load a playlist, upload MP3s to extract audio features, and get ranked transition suggestions scored on harmonic compatibility, BPM, and energy.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14 App Router, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.9+) |
| Audio analysis | librosa |
| Auth | Spotify Authorization Code Flow |

## Quick start

**Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in Spotify credentials
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:3000`.

## Environment variables (`backend/.env`)

```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
FRONTEND_URL=http://127.0.0.1:3000
```

Register `http://127.0.0.1:8000/auth/callback` as a redirect URI in your Spotify app dashboard. Use `127.0.0.1` — Spotify no longer accepts `localhost`.

## Scoring formula

```
score = 0.4 × key_score + 0.4 × bpm_score + 0.2 × energy_score
```

**Key score** (Camelot Wheel)

| Relationship | Score |
|---|---|
| Same key | 100 |
| Adjacent (±1) or same number | 85 |
| Relative major/minor | 75 |
| All else / unknown | 40 |

**BPM score**

| Delta | Score |
|---|---|
| ≤ 2 BPM | 100 |
| ≤ 5 BPM | 80 |
| ≤ 10 BPM | 60 |
| > 10 BPM | 30 |

**Energy score** (0.0 – 1.0)

| Delta | Score |
|---|---|
| < 0.1 | 100 |
| < 0.2 | 80 |
| < 0.3 | 60 |
| ≥ 0.3 | 40 (flagged as energy jump) |

## Audio analysis (librosa)

Because Spotify deprecated the `/audio-features` endpoint for apps created after November 2024, BPM, key, and energy must be extracted locally. Click the upload icon next to any track and select its MP3. The backend analyzes the first 60 seconds using:

- **BPM** — `librosa.beat.beat_track()`
- **Key / mode** — chroma features + Krumhansl-Schmuckler key profiles
- **Energy** — RMS amplitude normalized to 0 – 1

Results patch the track in state immediately. Upload the next track while the current one is playing to have scores ready before the transition.

## Known limitations (v1)

- Only playlists you **own** on Spotify can be loaded. Followed/shared playlists are blocked by Spotify's API for newer apps.
- Sessions are in-memory only — restarting the backend requires re-login.
- Audio features require a manual MP3 upload per track; there is no bulk import.

---

## Roadmap

### Planned — v2

- **Structural segment detection** — detect intro, verse, drop, breakdown, and outro boundaries using librosa's self-similarity matrix. Each segment will carry `{start, end, label, energy}` — the `segments` field is already returned by the analyze endpoint and ready to be populated.

- **Two-track transition analysis** — while track A plays, upload track B in the background. The transition scorer compares the outro of A against the intro of B directly rather than averaging over the whole track.

- **DJ practices guide** — a curated `docs/dj-practices.md` of transition heuristics (energy arcs, harmonic mixing rules, phrase alignment, beatmatching) that feed additional scoring weights.

### Planned — v3+

- **Lyrics-based semantic matching** — fetch lyrics via the Genius API, compare word themes and energy of the outro verse of track A against the intro verse of track B to find natural word-play or thematic transitions.

- **Segment labeling pipeline** — UI for a DJ to review auto-detected segments and apply labels. Labeled data trains a classifier to replace the heuristic approach.

- **Cross-track similarity fingerprints** — timbral + harmonic fingerprints per segment enable finding tracks where a specific breakdown sounds like another track's intro, going beyond BPM/key matching.

- **Followed playlist support** — contingent on Spotify restoring API access for newer apps or a workaround becoming available.

- **Set export** — save a curated run order back to Spotify as a new playlist.

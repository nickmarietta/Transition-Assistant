import type { PlaylistResponse, SpotifyUser, SuggestResponse, Track } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// --------------------------------------------------------------------------
// Session management — stored in sessionStorage, passed as ?session_id=
// --------------------------------------------------------------------------

export function storeSessionId(id: string) {
  sessionStorage.setItem("session_id", id);
}

export function clearSessionId() {
  sessionStorage.removeItem("session_id");
}

function getSessionId(): string | null {
  return sessionStorage.getItem("session_id");
}

// --------------------------------------------------------------------------
// Core fetch helper
// --------------------------------------------------------------------------

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const sid = getSessionId();
  const sep = path.includes("?") ? "&" : "?";
  const url = sid ? `${API}${path}${sep}session_id=${sid}` : `${API}${path}`;

  const res = await fetch(url, init);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "API error");
  }
  return res.json();
}

// --------------------------------------------------------------------------
// Auth
// --------------------------------------------------------------------------

export function login() {
  window.location.href = `${API}/auth/login`;
}

export async function getAuthStatus(): Promise<{ logged_in: boolean }> {
  const sid = getSessionId();
  if (!sid) return { logged_in: false };
  return apiFetch("/auth/status");
}

export async function getProfile(): Promise<SpotifyUser> {
  return apiFetch("/auth/me");
}

export async function logout(): Promise<void> {
  await apiFetch("/auth/logout", { method: "POST" });
  clearSessionId();
}

// --------------------------------------------------------------------------
// Playlist + scoring
// --------------------------------------------------------------------------

export async function fetchPlaylist(url: string): Promise<PlaylistResponse> {
  return apiFetch(`/playlist?url=${encodeURIComponent(url)}`);
}

export async function getSuggestions(
  currentTrackId: string,
  tracks: Track[]
): Promise<SuggestResponse> {
  return apiFetch("/scoring/suggest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ current_track_id: currentTrackId, tracks }),
  });
}

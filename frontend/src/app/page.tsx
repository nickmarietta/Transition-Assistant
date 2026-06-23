"use client";

import { useEffect, useState } from "react";
import {
  getAuthStatus,
  getProfile,
  login,
  logout,
  fetchPlaylist,
  getSuggestions,
  storeSessionId,
} from "@/lib/api";
import type { SpotifyUser, Track, ScoreSuggestion } from "@/lib/types";
import PlaylistInput from "@/components/PlaylistInput";
import TrackList from "@/components/TrackList";

export default function Home() {
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null);
  const [profile, setProfile] = useState<SpotifyUser | null>(null);
  const [playlistName, setPlaylistName] = useState<string | null>(null);
  const [tracks, setTracks] = useState<Track[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<ScoreSuggestion[]>([]);
  const [loadingPlaylist, setLoadingPlaylist] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // After OAuth the backend redirects to /?session_id=<uuid>
    // Extract it, persist it, then clean the URL
    const params = new URLSearchParams(window.location.search);
    const sid = params.get("session_id");
    if (sid) {
      storeSessionId(sid);
      window.history.replaceState({}, "", "/");
    }

    getAuthStatus().then((s) => {
      setLoggedIn(s.logged_in);
      if (s.logged_in) {
        getProfile()
          .then(setProfile)
          .catch(() => null);
      }
    }).catch(() => setLoggedIn(false));
  }, []);

  async function handleLoadPlaylist(url: string) {
    setError(null);
    setLoadingPlaylist(true);
    setTracks([]);
    setSelectedId(null);
    setSuggestions([]);
    try {
      const data = await fetchPlaylist(url);
      setPlaylistName(data.name);
      setTracks(data.tracks);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load playlist");
    } finally {
      setLoadingPlaylist(false);
    }
  }

  async function handleSelectTrack(id: string) {
    setSelectedId(id);
    setLoadingSuggestions(true);
    setSuggestions([]);
    try {
      const data = await getSuggestions(id, tracks);
      setSuggestions(data.suggestions);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to score tracks");
    } finally {
      setLoadingSuggestions(false);
    }
  }

  async function handleLogout() {
    await logout();
    setLoggedIn(false);
    setProfile(null);
    setTracks([]);
    setPlaylistName(null);
    setSelectedId(null);
    setSuggestions([]);
  }

  if (loggedIn === null) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-zinc-500">Loading…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">
          DJ Transition Assistant
        </h1>
        {loggedIn && profile && (
          <div className="flex items-center gap-3">
            {profile.image_url ? (
              <img
                src={profile.image_url}
                alt={profile.display_name}
                className="h-8 w-8 rounded-full object-cover ring-1 ring-zinc-600"
              />
            ) : (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-600 text-xs font-bold uppercase">
                {profile.display_name.charAt(0)}
              </div>
            )}
            <span className="text-sm text-zinc-300">{profile.display_name}</span>
            <button
              onClick={handleLogout}
              className="rounded-lg bg-zinc-800 px-3 py-1.5 text-sm hover:bg-zinc-700"
            >
              Log out
            </button>
          </div>
        )}
      </header>

      {!loggedIn ? (
        <div className="flex flex-col items-center gap-4 py-24">
          <p className="text-zinc-400">
            Connect your Spotify account to get started.
          </p>
          <button
            onClick={login}
            className="rounded-full bg-green-500 px-8 py-3 font-semibold text-black hover:bg-green-400"
          >
            Login with Spotify
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <PlaylistInput onLoad={handleLoadPlaylist} loading={loadingPlaylist} />

          {error && <p className="text-sm text-red-400">{error}</p>}

          {playlistName && (
            <p className="text-sm text-zinc-400">
              Loaded:{" "}
              <span className="font-medium text-white">{playlistName}</span>{" "}
              ({tracks.length} tracks)
            </p>
          )}

          {tracks.length > 0 && (
            <TrackList
              tracks={tracks}
              selectedId={selectedId}
              suggestions={suggestions}
              loadingSuggestions={loadingSuggestions}
              onSelectTrack={handleSelectTrack}
            />
          )}
        </div>
      )}
    </main>
  );
}

"use client";

import { useEffect, useState } from "react";
import {
  getAuthStatus,
  getProfile,
  login,
  logout,
  fetchPlaylist,
  fetchDemoPlaylist,
  getSuggestions,
  analyzeTrack,
  storeSessionId,
} from "@/lib/api";
import type { SpotifyUser, Track, ScoreSuggestion } from "@/lib/types";
import PlaylistInput from "@/components/PlaylistInput";
import NowPlaying from "@/components/NowPlaying";
import TrackList from "@/components/TrackList";

export default function Home() {
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null);
  const [profile, setProfile] = useState<SpotifyUser | null>(null);
  const [playlistName, setPlaylistName] = useState<string | null>(null);
  const [tracks, setTracks] = useState<Track[]>([]);
  const [nowPlayingId, setNowPlayingId] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<ScoreSuggestion[]>([]);
  const [loadingPlaylist, setLoadingPlaylist] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [analyzingIds, setAnalyzingIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sid = params.get("session_id");
    if (sid) {
      storeSessionId(sid);
      window.history.replaceState({}, "", "/");
    }
    getAuthStatus().then((s) => {
      setLoggedIn(s.logged_in);
      if (s.logged_in) getProfile().then(setProfile).catch(() => null);
    }).catch(() => setLoggedIn(false));
  }, []);

  async function handleLoadPlaylist(url: string) {
    setError(null);
    setLoadingPlaylist(true);
    setTracks([]);
    setNowPlayingId(null);
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

  async function handleLoadDemo() {
    setError(null);
    setLoadingPlaylist(true);
    setTracks([]);
    setNowPlayingId(null);
    setSuggestions([]);
    try {
      const data = await fetchDemoPlaylist();
      setPlaylistName(data.name);
      setTracks(data.tracks);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load demo");
    } finally {
      setLoadingPlaylist(false);
    }
  }

  async function handleSetNowPlaying(id: string) {
    setNowPlayingId(id);
    setLoadingSuggestions(true);
    setSuggestions([]);
    setError(null);
    try {
      const data = await getSuggestions(id, tracks);
      setSuggestions(data.suggestions);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to score tracks");
    } finally {
      setLoadingSuggestions(false);
    }
  }

  async function handleAnalyzeTrack(id: string, file: File) {
    setAnalyzingIds((prev) => new Set(prev).add(id));
    setError(null);
    try {
      const analysis = await analyzeTrack(file);
      setTracks((prev) =>
        prev.map((t) =>
          t.id === id
            ? { ...t, bpm: analysis.bpm, key: analysis.key, mode: analysis.mode, energy: analysis.energy, camelot: analysis.camelot }
            : t
        )
      );
      // Re-score if this is the Now Playing track so suggestions update immediately
      if (id === nowPlayingId) {
        const updated = tracks.map((t) =>
          t.id === id
            ? { ...t, bpm: analysis.bpm, key: analysis.key, mode: analysis.mode, energy: analysis.energy, camelot: analysis.camelot }
            : t
        );
        setLoadingSuggestions(true);
        const data = await getSuggestions(id, updated);
        setSuggestions(data.suggestions);
        setLoadingSuggestions(false);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Audio analysis failed");
    } finally {
      setAnalyzingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }

  async function handleLogout() {
    await logout();
    setLoggedIn(false);
    setProfile(null);
    setTracks([]);
    setPlaylistName(null);
    setNowPlayingId(null);
    setSuggestions([]);
  }

  const nowPlayingTrack = tracks.find((t) => t.id === nowPlayingId) ?? null;

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
        <h1 className="text-2xl font-bold tracking-tight">DJ Transition Assistant</h1>
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
          <p className="text-zinc-400">Connect your Spotify account to get started.</p>
          <button
            onClick={login}
            className="rounded-full bg-green-500 px-8 py-3 font-semibold text-black hover:bg-green-400"
          >
            Login with Spotify
          </button>
          <div className="flex items-center gap-3 text-sm text-zinc-500">
            <span className="h-px w-16 bg-zinc-700" />
            or
            <span className="h-px w-16 bg-zinc-700" />
          </div>
          <button
            onClick={handleLoadDemo}
            disabled={loadingPlaylist}
            className="rounded-full border border-zinc-700 px-6 py-2 text-sm text-zinc-300 hover:border-zinc-500 hover:text-white transition-colors disabled:opacity-50"
          >
            {loadingPlaylist ? "Loading…" : "Try the demo (no login needed)"}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Playlist loader — collapses to a label once loaded */}
          {playlistName ? (
            <div className="flex items-center justify-between rounded-lg bg-zinc-800 px-4 py-2 text-sm">
              <span className="text-zinc-400">
                Playlist: <span className="font-medium text-white">{playlistName}</span>
                <span className="ml-2 text-zinc-500">({tracks.length} tracks)</span>
              </span>
              <button
                onClick={() => {
                  setPlaylistName(null);
                  setTracks([]);
                  setNowPlayingId(null);
                  setSuggestions([]);
                }}
                className="text-xs text-zinc-500 hover:text-white transition-colors"
              >
                Change playlist
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <PlaylistInput onLoad={handleLoadPlaylist} loading={loadingPlaylist} />
              <button
                onClick={handleLoadDemo}
                disabled={loadingPlaylist}
                className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors disabled:opacity-50"
              >
                or load the demo set →
              </button>
            </div>
          )}

          {error && <p className="text-sm text-red-400">{error}</p>}

          {tracks.length > 0 && (
            <>
              <NowPlaying
                track={nowPlayingTrack}
                analyzing={analyzingIds.has(nowPlayingId ?? "")}
                onUpload={(file) => nowPlayingId && handleAnalyzeTrack(nowPlayingId, file)}
              />

              <TrackList
                tracks={tracks}
                nowPlayingId={nowPlayingId}
                suggestions={suggestions}
                loadingSuggestions={loadingSuggestions}
                analyzingIds={analyzingIds}
                onSetNowPlaying={handleSetNowPlaying}
                onAnalyzeTrack={handleAnalyzeTrack}
              />
            </>
          )}
        </div>
      )}
    </main>
  );
}

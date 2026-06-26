"use client";

import { useRef } from "react";
import type { Track, ScoreSuggestion } from "@/lib/types";
import { keyName } from "@/lib/utils";
import TrackCard from "./TrackCard";
import CamelotWheel from "./CamelotWheel";

interface Props {
  tracks: Track[];
  nowPlayingId: string | null;
  suggestions: ScoreSuggestion[];
  loadingSuggestions: boolean;
  analyzingIds: Set<string>;
  onSetNowPlaying: (id: string) => void;
  onAnalyzeTrack: (id: string, file: File) => void;
}

function UploadIcon({ spinning }: { spinning: boolean }) {
  if (spinning) {
    return (
      <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
      </svg>
    );
  }
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 12V4m0 0L8 8m4-4l4 4" />
    </svg>
  );
}

function TrackRow({
  track,
  isNowPlaying,
  analyzing,
  onSelect,
  onAnalyze,
}: {
  track: Track;
  isNowPlaying: boolean;
  analyzing: boolean;
  onSelect: () => void;
  onAnalyze: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={onSelect}
        className={`flex-1 min-w-0 text-left rounded-lg px-3 py-2 text-sm transition-colors ${
          isNowPlaying
            ? "bg-green-600 text-white"
            : "bg-zinc-800 hover:bg-zinc-700"
        }`}
      >
        <p className="truncate font-medium">{track.name}</p>
        <p className="truncate text-xs opacity-70">{track.artist}</p>
        <div className="flex flex-wrap gap-2 mt-0.5">
          {track.camelot && (
            <span className="text-xs opacity-60">{track.camelot}</span>
          )}
          {keyName(track.key, track.mode) && (
            <span className="text-xs opacity-50">{keyName(track.key, track.mode)}</span>
          )}
          {track.bpm != null && (
            <span className="text-xs opacity-60">{track.bpm.toFixed(1)} BPM</span>
          )}
          {track.energy != null && (
            <span className="text-xs opacity-60">
              E {Math.round(track.energy * 100)}%
            </span>
          )}
        </div>
      </button>

      <button
        title={analyzing ? "Analyzing…" : track.bpm != null ? "Re-analyze" : "Upload MP3 to analyze BPM & key"}
        disabled={analyzing}
        onClick={() => inputRef.current?.click()}
        className={`shrink-0 rounded p-1.5 transition-colors ${
          analyzing
            ? "text-zinc-500 cursor-not-allowed"
            : track.bpm != null
            ? "text-green-400 hover:text-white hover:bg-zinc-700"
            : "text-zinc-400 hover:text-white hover:bg-zinc-700"
        }`}
      >
        <UploadIcon spinning={analyzing} />
      </button>

      <input
        ref={inputRef}
        type="file"
        accept="audio/*"
        className="sr-only"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onAnalyze(file);
          e.target.value = "";
        }}
      />
    </div>
  );
}

export default function TrackList({
  tracks,
  nowPlayingId,
  suggestions,
  loadingSuggestions,
  analyzingIds,
  onSetNowPlaying,
  onAnalyzeTrack,
}: Props) {
  const nowPlayingTrack = tracks.find((t) => t.id === nowPlayingId) ?? null;

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      {/* ── Candidates ── */}
      <div>
        <h2 className="mb-1 text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Playlist — candidates
        </h2>
        <p className="mb-3 text-xs text-zinc-500">
          Click a track to set it as Now Playing. Use ↑ to analyze BPM & key.
        </p>
        <div className="space-y-1 max-h-[65vh] overflow-y-auto pr-1">
          {tracks.map((track) => (
            <TrackRow
              key={track.id}
              track={track}
              isNowPlaying={track.id === nowPlayingId}
              analyzing={analyzingIds.has(track.id)}
              onSelect={() => onSetNowPlaying(track.id)}
              onAnalyze={(file) => onAnalyzeTrack(track.id, file)}
            />
          ))}
        </div>
      </div>

      {/* ── Wheel + Suggestions ── */}
      <div className="flex flex-col gap-4">
        <CamelotWheel currentTrack={nowPlayingTrack} suggestions={suggestions} />

        <div>
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Best next tracks
          </h2>

          {!nowPlayingId && (
            <p className="text-zinc-500 text-sm">
              Set a Now Playing track to see transition suggestions.
            </p>
          )}
          {loadingSuggestions && (
            <p className="text-zinc-500 text-sm">Scoring…</p>
          )}
          {nowPlayingId && !loadingSuggestions && suggestions.length === 0 && (
            <p className="text-zinc-500 text-sm">
              No suggestions yet — try uploading the MP3 to get key & BPM data.
            </p>
          )}

          <div className="space-y-2 max-h-[45vh] overflow-y-auto pr-1">
            {suggestions.map((s) => (
              <TrackCard
                key={s.track.id}
                suggestion={s}
                onSetNowPlaying={onSetNowPlaying}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

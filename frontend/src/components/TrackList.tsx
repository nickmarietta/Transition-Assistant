"use client";

import type { Track, ScoreSuggestion } from "@/lib/types";
import TrackCard from "./TrackCard";

interface Props {
  tracks: Track[];
  selectedId: string | null;
  suggestions: ScoreSuggestion[];
  loadingSuggestions: boolean;
  onSelectTrack: (id: string) => void;
}

export default function TrackList({
  tracks,
  selectedId,
  suggestions,
  loadingSuggestions,
  onSelectTrack,
}: Props) {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      {/* Track picker */}
      <div>
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Playlist — click to set current track
        </h2>
        <div className="space-y-1 max-h-[70vh] overflow-y-auto pr-1">
          {tracks.map((track) => (
            <button
              key={track.id}
              onClick={() => onSelectTrack(track.id)}
              className={`w-full text-left rounded-lg px-3 py-2 text-sm transition-colors ${
                selectedId === track.id
                  ? "bg-green-600 text-white"
                  : "bg-zinc-800 hover:bg-zinc-700"
              }`}
            >
              <p className="truncate font-medium">{track.name}</p>
              <p className="truncate text-xs opacity-70">{track.artist}</p>
              <div className="flex gap-2 mt-0.5">
                {track.camelot && (
                  <span className="text-xs opacity-60">{track.camelot}</span>
                )}
                {track.bpm != null && (
                  <span className="text-xs opacity-60">{Math.round(track.bpm)} BPM</span>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Suggestions */}
      <div>
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Best next tracks
        </h2>
        {!selectedId && (
          <p className="text-zinc-500 text-sm">
            Select a track on the left to see suggestions.
          </p>
        )}
        {loadingSuggestions && (
          <p className="text-zinc-500 text-sm">Scoring…</p>
        )}
        {selectedId && !loadingSuggestions && suggestions.length === 0 && (
          <p className="text-zinc-500 text-sm">No suggestions — track may be missing audio features.</p>
        )}
        <div className="space-y-2 max-h-[70vh] overflow-y-auto pr-1">
          {suggestions.map((s) => (
            <TrackCard key={s.track.id} suggestion={s} />
          ))}
        </div>
      </div>
    </div>
  );
}

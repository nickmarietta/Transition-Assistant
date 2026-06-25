"use client";

import { useRef } from "react";
import type { Track } from "@/lib/types";

interface Props {
  track: Track | null;
  analyzing: boolean;
  onUpload: (file: File) => void;
}

export default function NowPlaying({ track, analyzing, onUpload }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const isAnalyzed = track?.bpm != null;

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-green-500">
        ▶ Now Playing
      </p>

      {track ? (
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="truncate text-lg font-bold">{track.name}</p>
            <p className="truncate text-sm text-zinc-400">{track.artist}</p>

            <div className="mt-2 flex flex-wrap gap-2">
              {track.camelot ? (
                <span className="rounded bg-green-900/50 px-2 py-0.5 text-xs font-semibold text-green-300">
                  {track.camelot}
                </span>
              ) : (
                <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-500">
                  Key unknown
                </span>
              )}
              {track.bpm != null ? (
                <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300">
                  {Math.round(track.bpm)} BPM
                </span>
              ) : (
                <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-500">
                  BPM unknown
                </span>
              )}
              {track.energy != null && (
                <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300">
                  Energy {Math.round(track.energy * 100)}%
                </span>
              )}
            </div>
          </div>

          <div className="shrink-0">
            {isAnalyzed ? (
              <button
                onClick={() => inputRef.current?.click()}
                disabled={analyzing}
                className="flex items-center gap-1.5 rounded-lg bg-zinc-800 px-3 py-1.5 text-xs text-green-400 hover:bg-zinc-700 disabled:opacity-50 transition-colors"
              >
                {analyzing ? "Analyzing…" : "✓ Analyzed — re-upload"}
              </button>
            ) : (
              <button
                onClick={() => inputRef.current?.click()}
                disabled={analyzing}
                className="flex items-center gap-2 rounded-lg bg-green-600 px-3 py-2 text-xs font-semibold text-white hover:bg-green-500 disabled:opacity-60 transition-colors"
              >
                {analyzing ? "Analyzing…" : "Upload MP3 to analyze"}
              </button>
            )}
            <input
              ref={inputRef}
              type="file"
              accept="audio/*"
              className="sr-only"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) onUpload(file);
                e.target.value = "";
              }}
            />
          </div>
        </div>
      ) : (
        <p className="text-sm text-zinc-500">
          Click any track in the playlist below to set it as Now Playing.
        </p>
      )}
    </div>
  );
}

import type { ScoreSuggestion } from "@/lib/types";

function scoreColor(score: number) {
  if (score >= 80) return "text-green-400";
  if (score >= 60) return "text-yellow-400";
  return "text-red-400";
}

interface Props {
  suggestion: ScoreSuggestion;
  onSetNowPlaying: (id: string) => void;
}

export default function TrackCard({ suggestion, onSetNowPlaying }: Props) {
  const { track, score, key_score, bpm_score, energy_score, energy_jump } = suggestion;

  return (
    <div className="flex items-center gap-3 rounded-lg bg-zinc-800 p-3 hover:bg-zinc-700 transition-colors">
      <div className="flex flex-col items-center w-12 shrink-0">
        <span className={`text-xl font-bold tabular-nums ${scoreColor(score)}`}>
          {score.toFixed(0)}
        </span>
        <span className="text-xs text-zinc-500">score</span>
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{track.name}</p>
        <p className="truncate text-sm text-zinc-400">{track.artist}</p>
        <div className="mt-0.5 flex flex-wrap gap-1.5">
          {track.camelot && (
            <span className="rounded bg-zinc-700 px-1.5 py-0.5 text-xs">{track.camelot}</span>
          )}
          {track.bpm != null && (
            <span className="rounded bg-zinc-700 px-1.5 py-0.5 text-xs">
              {Math.round(track.bpm)} BPM
            </span>
          )}
          {energy_jump && (
            <span className="rounded bg-orange-900 px-1.5 py-0.5 text-xs text-orange-300">
              energy jump
            </span>
          )}
        </div>
      </div>

      <div className="hidden lg:grid grid-cols-3 gap-1 text-center text-xs w-24 shrink-0">
        <div>
          <div className={scoreColor(key_score)}>{key_score}</div>
          <div className="text-zinc-500">key</div>
        </div>
        <div>
          <div className={scoreColor(bpm_score)}>{bpm_score}</div>
          <div className="text-zinc-500">bpm</div>
        </div>
        <div>
          <div className={scoreColor(energy_score)}>{energy_score}</div>
          <div className="text-zinc-500">nrg</div>
        </div>
      </div>

      <button
        onClick={() => onSetNowPlaying(track.id)}
        title="Set as Now Playing"
        className="shrink-0 rounded-lg p-2 text-zinc-500 hover:text-green-400 hover:bg-zinc-600 transition-colors"
      >
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M8 5v14l11-7z" />
        </svg>
      </button>
    </div>
  );
}

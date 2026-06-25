"use client";

import type { Track, ScoreSuggestion } from "@/lib/types";

// ── geometry ──────────────────────────────────────────────────────────────────
const SIZE = 320;
const CX = SIZE / 2;
const CY = SIZE / 2;
const R_B_OUT = 152;  // major (B) ring outer edge
const R_B_IN  = 104;  // major inner / minor outer boundary
const R_A_IN  = 58;   // minor (A) ring inner edge
const R_CTR   = 54;   // center disc

const POSITIONS = Array.from({ length: 12 }, (_, i) => i + 1);

function rad(deg: number) {
  return (deg * Math.PI) / 180;
}

// Position 12 → 0 ° (12-o'clock), 1 → 30 °, 2 → 60 °, … (clockwise)
function centerDeg(pos: number) {
  return (pos % 12) * 30;
}

function arcPath(pos: number, rIn: number, rOut: number): string {
  const GAP = 1.5; // degrees of gap between adjacent sectors
  const s = rad(centerDeg(pos) - 15 + GAP);
  const e = rad(centerDeg(pos) + 15 - GAP);

  const x1 = CX + rOut * Math.sin(s), y1 = CY - rOut * Math.cos(s);
  const x2 = CX + rOut * Math.sin(e), y2 = CY - rOut * Math.cos(e);
  const x3 = CX + rIn  * Math.sin(e), y3 = CY - rIn  * Math.cos(e);
  const x4 = CX + rIn  * Math.sin(s), y4 = CY - rIn  * Math.cos(s);

  const f = (n: number) => n.toFixed(2);
  return [
    `M ${f(x1)} ${f(y1)}`,
    `A ${rOut} ${rOut} 0 0 1 ${f(x2)} ${f(y2)}`,
    `L ${f(x3)} ${f(y3)}`,
    `A ${rIn} ${rIn} 0 0 0 ${f(x4)} ${f(y4)}`,
    "Z",
  ].join(" ");
}

function labelXY(pos: number, rMid: number): [number, number] {
  const a = rad(centerDeg(pos));
  return [CX + rMid * Math.sin(a), CY - rMid * Math.cos(a)];
}

// ── color helpers ─────────────────────────────────────────────────────────────
const DEFAULT_B  = "#27272a"; // zinc-800  (major ring default)
const DEFAULT_A  = "#1f1f23"; // slightly darker (minor ring default)
const CURRENT    = "#16a34a"; // green-600
const HIGH_FILL  = "#064e3b"; // emerald-900 — score ≥ 80
const MED_FILL   = "#431407"; // amber-950  — score 60-79
const HIGH_TEXT  = "#6ee7b7"; // emerald-300
const MED_TEXT   = "#fcd34d"; // amber-300
const DIM_TEXT   = "#52525b"; // zinc-600

function cellColors(
  key: string,
  currentCamelot: string | null,
  scoreMap: Map<string, number>,
  isB: boolean,
): { fill: string; text: string; weight: string } {
  if (key === currentCamelot) {
    return { fill: CURRENT, text: "#ffffff", weight: "700" };
  }
  const score = scoreMap.get(key);
  if (score === undefined) {
    return { fill: isB ? DEFAULT_B : DEFAULT_A, text: DIM_TEXT, weight: "400" };
  }
  if (score >= 80) return { fill: HIGH_FILL, text: HIGH_TEXT, weight: "600" };
  if (score >= 60) return { fill: MED_FILL,  text: MED_TEXT,  weight: "600" };
  return { fill: isB ? DEFAULT_B : DEFAULT_A, text: DIM_TEXT, weight: "400" };
}

// ── component ─────────────────────────────────────────────────────────────────
interface Props {
  currentTrack: Track | null;
  suggestions: ScoreSuggestion[];
}

export default function CamelotWheel({ currentTrack, suggestions }: Props) {
  const currentCamelot = currentTrack?.camelot ?? null;

  // Best score per camelot position among all suggestions
  const scoreMap = new Map<string, number>();
  for (const s of suggestions) {
    if (!s.track.camelot) continue;
    const prev = scoreMap.get(s.track.camelot) ?? 0;
    if (s.score > prev) scoreMap.set(s.track.camelot, s.score);
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <svg
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        className="w-full max-w-[280px]"
        aria-label="Camelot Wheel"
      >
        {/* ── B ring (major, outer) ── */}
        {POSITIONS.map((pos) => {
          const key = `${pos}B`;
          const { fill, text, weight } = cellColors(key, currentCamelot, scoreMap, true);
          const [tx, ty] = labelXY(pos, (R_B_OUT + R_B_IN) / 2);
          return (
            <g key={key}>
              <path d={arcPath(pos, R_B_IN, R_B_OUT)} fill={fill} />
              <text
                x={tx} y={ty}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="11"
                fontWeight={weight}
                fill={text}
                style={{ userSelect: "none" }}
              >
                {key}
              </text>
            </g>
          );
        })}

        {/* ── A ring (minor, inner) ── */}
        {POSITIONS.map((pos) => {
          const key = `${pos}A`;
          const { fill, text, weight } = cellColors(key, currentCamelot, scoreMap, false);
          const [tx, ty] = labelXY(pos, (R_B_IN + R_A_IN) / 2);
          return (
            <g key={key}>
              <path d={arcPath(pos, R_A_IN, R_B_IN)} fill={fill} />
              <text
                x={tx} y={ty}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="10"
                fontWeight={weight}
                fill={text}
                style={{ userSelect: "none" }}
              >
                {key}
              </text>
            </g>
          );
        })}

        {/* ── Dividing ring between B and A ── */}
        <circle
          cx={CX} cy={CY} r={R_B_IN}
          fill="none"
          stroke="#09090b"
          strokeWidth="2"
        />

        {/* ── Center disc ── */}
        <circle cx={CX} cy={CY} r={R_CTR} fill="#09090b" />

        {currentCamelot ? (
          <>
            <text
              x={CX} y={CY - 9}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="22"
              fontWeight="700"
              fill="#16a34a"
              style={{ userSelect: "none" }}
            >
              {currentCamelot}
            </text>
            <text
              x={CX} y={CY + 14}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="8.5"
              fill="#71717a"
              style={{ userSelect: "none" }}
            >
              {(currentTrack?.name ?? "").slice(0, 18)}
            </text>
          </>
        ) : (
          <text
            x={CX} y={CY}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="10"
            fill="#52525b"
            style={{ userSelect: "none" }}
          >
            select a track
          </text>
        )}
      </svg>

      {/* Legend */}
      <div className="flex gap-4 text-xs text-zinc-500">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-green-600" />
          Current
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-emerald-900" />
          Score 80+
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-amber-950" />
          Score 60–79
        </span>
      </div>
    </div>
  );
}

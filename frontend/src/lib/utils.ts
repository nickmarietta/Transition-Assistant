const NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];

/** Convert a Spotify key (0-11) + mode (0=minor, 1=major) to a human-readable name. */
export function keyName(key: number | null | undefined, mode: number | null | undefined): string {
  if (key == null || mode == null || key === -1) return '';
  return `${NOTE_NAMES[key]} ${mode === 1 ? 'major' : 'minor'}`;
}

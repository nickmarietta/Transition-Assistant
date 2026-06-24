export interface SpotifyUser {
  id: string;
  display_name: string;
  email: string | null;
  image_url: string | null;
}

export interface Track {
  id: string;
  name: string;
  artist: string;
  duration_ms: number | null;
  key: number;
  mode: number;
  bpm: number | null;
  energy: number | null;
  camelot: string | null;
}

export interface PlaylistResponse {
  id: string;
  name: string;
  track_count: number;
  tracks: Track[];
}

export interface ScoreSuggestion {
  track: Track;
  score: number;
  key_score: number;
  bpm_score: number;
  energy_score: number;
  energy_jump: boolean;
}

export interface SuggestResponse {
  suggestions: ScoreSuggestion[];
}

export interface Segment {
  start: number;
  end: number;
  label: string | null;
  energy: number;
}

export interface AudioAnalysis {
  bpm: number;
  key: number;
  mode: number;
  energy: number;
  camelot: string | null;
  segments: Segment[];
}

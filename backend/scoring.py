"""
Scoring engine for DJ transitions.

Compatibility score = 0.4 * key_score + 0.4 * bpm_score + 0.2 * energy_score
"""
from __future__ import annotations

# Maps (spotify_key, spotify_mode) → Camelot notation string
# spotify_key: 0=C, 1=C#, 2=D, 3=Eb, 4=E, 5=F, 6=F#, 7=G,
#              8=Ab, 9=A, 10=Bb, 11=B; mode: 0=minor, 1=major
CAMELOT: dict[tuple[int, int], str] = {
    (0, 1): "8B",
    (1, 1): "3B",
    (2, 1): "10B",
    (3, 1): "5B",
    (4, 1): "12B",
    (5, 1): "7B",
    (6, 1): "2B",
    (7, 1): "9B",
    (8, 1): "4B",
    (9, 1): "11B",
    (10, 1): "6B",
    (11, 1): "1B",
    (0, 0): "5A",
    (1, 0): "12A",
    (2, 0): "7A",
    (3, 0): "2A",
    (4, 0): "9A",
    (5, 0): "4A",
    (6, 0): "11A",
    (7, 0): "6A",
    (8, 0): "1A",
    (9, 0): "8A",
    (10, 0): "3A",
    (11, 0): "10A",
}

# "8B" → (8, "B"), "12A" → (12, "A")
_COORDS: dict[str, tuple[int, str]] = {
    v: (int(v[:-1]), v[-1]) for v in CAMELOT.values()
}


def camelot_distance(a: str, b: str) -> int:
    """Minimum steps between two Camelot positions on the wheel.

    A step is either a number move of ±1 around the 12-position circle
    (same letter) or a letter switch A↔B (same number).
    Returns 0 for identical, 1 for adjacent or relative, ≥2 otherwise.
    """
    if a == b:
        return 0
    num_a, letter_a = _COORDS[a]
    num_b, letter_b = _COORDS[b]
    diff = abs(num_a - num_b)
    circ = min(diff, 12 - diff)        # shortest arc on the 12-position circle
    letter_cost = 0 if letter_a == letter_b else 1
    return circ + letter_cost


def _key_score(camelot_a: str | None, camelot_b: str | None) -> int:
    if camelot_a is None or camelot_b is None:
        return 40
    if camelot_a == camelot_b:
        return 100
    num_a, letter_a = _COORDS[camelot_a]
    num_b, letter_b = _COORDS[camelot_b]
    if num_a == num_b:
        return 75                      # relative major/minor (same number, A↔B)
    diff = abs(num_a - num_b)
    if min(diff, 12 - diff) == 1 and letter_a == letter_b:
        return 85                      # adjacent on the wheel (±1, same letter)
    return 40


def _bpm_score(bpm_a: float | None, bpm_b: float | None) -> int:
    if bpm_a is None or bpm_b is None:
        return 30
    delta = abs(bpm_a - bpm_b)
    if delta <= 2:
        return 100
    if delta <= 5:
        return 80
    if delta <= 10:
        return 60
    return 30


def _energy_score(energy_a: float | None, energy_b: float | None) -> tuple[int, bool]:
    if energy_a is None or energy_b is None:
        return 40, False
    delta = abs(energy_a - energy_b)
    if delta < 0.1:
        return 100, False
    if delta < 0.2:
        return 80, False
    if delta < 0.3:
        return 60, False
    return 40, True


def score_transition(track_a: dict, track_b: dict) -> dict:
    """Score the compatibility of transitioning from track_a to track_b.

    Each track dict must have:
        key    (int, -1 if unknown)
        mode   (int, 0=minor / 1=major)
        bpm    (float)
        energy (float, 0.0–1.0)

    Returns:
        score        – weighted total (0–100)
        key_score    – 100 / 85 / 75 / 40
        bpm_score    – 100 / 80 / 60 / 30
        energy_score – 100 / 80 / 60 / 40
        energy_jump  – True when energy delta ≥ 0.3
    """
    key_a = track_a.get("key", -1)
    key_b = track_b.get("key", -1)
    camelot_a = CAMELOT.get((key_a, track_a.get("mode", 1))) if key_a != -1 else None
    camelot_b = CAMELOT.get((key_b, track_b.get("mode", 1))) if key_b != -1 else None

    ks = _key_score(camelot_a, camelot_b)
    bs = _bpm_score(track_a["bpm"], track_b["bpm"])
    es, energy_jump = _energy_score(track_a["energy"], track_b["energy"])

    return {
        "score": round(0.4 * ks + 0.4 * bs + 0.2 * es, 1),
        "key_score": ks,
        "bpm_score": bs,
        "energy_score": es,
        "energy_jump": energy_jump,
    }

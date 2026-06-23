from __future__ import annotations

# Maps (spotify_key, spotify_mode) → (camelot_number, camelot_letter)
# spotify_key: 0=C … 11=B, -1=unknown; mode: 0=minor, 1=major
CAMELOT: dict[tuple[int, int], tuple[int, str]] = {
    (0, 1): (8, "B"),   # C major
    (1, 1): (3, "B"),   # C# major
    (2, 1): (10, "B"),  # D major
    (3, 1): (5, "B"),   # Eb major
    (4, 1): (12, "B"),  # E major
    (5, 1): (7, "B"),   # F major
    (6, 1): (2, "B"),   # F# major
    (7, 1): (9, "B"),   # G major
    (8, 1): (4, "B"),   # Ab major
    (9, 1): (11, "B"),  # A major
    (10, 1): (6, "B"),  # Bb major
    (11, 1): (1, "B"),  # B major
    (0, 0): (5, "A"),   # C minor
    (1, 0): (12, "A"),  # C# minor
    (2, 0): (7, "A"),   # D minor
    (3, 0): (2, "A"),   # Eb minor
    (4, 0): (9, "A"),   # E minor
    (5, 0): (4, "A"),   # F minor
    (6, 0): (11, "A"),  # F# minor
    (7, 0): (6, "A"),   # G minor
    (8, 0): (1, "A"),   # Ab minor
    (9, 0): (8, "A"),   # A minor
    (10, 0): (3, "A"),  # Bb minor
    (11, 0): (10, "A"), # B minor
}


def key_score(key_a: int, mode_a: int, key_b: int, mode_b: int) -> int:
    if key_a == -1 or key_b == -1:
        return 40
    ca = CAMELOT.get((key_a, mode_a))
    cb = CAMELOT.get((key_b, mode_b))
    if ca is None or cb is None:
        return 40
    num_a, letter_a = ca
    num_b, letter_b = cb
    if num_a == num_b and letter_a == letter_b:
        return 100
    if num_a == num_b:
        return 75  # relative major/minor, same Camelot number
    if letter_a == letter_b:
        diff = abs(num_a - num_b)
        if diff == 1 or diff == 11:  # 11 handles 1↔12 wrap
            return 85
    return 40


def bpm_score(bpm_a: float, bpm_b: float) -> int:
    delta = abs(bpm_a - bpm_b)
    if delta <= 2:
        return 100
    if delta <= 5:
        return 80
    if delta <= 10:
        return 60
    return 30


def energy_score(energy_a: float, energy_b: float) -> tuple[int, bool]:
    delta = abs(energy_a - energy_b)
    if delta < 0.1:
        return 100, False
    if delta < 0.2:
        return 80, False
    if delta < 0.3:
        return 60, False
    return 40, True


def compatibility_score(
    key_a: int, mode_a: int, bpm_a: float, energy_a: float,
    key_b: int, mode_b: int, bpm_b: float, energy_b: float,
) -> dict:
    ks = key_score(key_a, mode_a, key_b, mode_b)
    bs = bpm_score(bpm_a, bpm_b)
    es, energy_jump = energy_score(energy_a, energy_b)
    total = round(0.4 * ks + 0.4 * bs + 0.2 * es, 1)
    return {
        "score": total,
        "key_score": ks,
        "bpm_score": bs,
        "energy_score": es,
        "energy_jump": energy_jump,
    }

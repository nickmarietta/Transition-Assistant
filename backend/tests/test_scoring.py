import pytest
from scoring import CAMELOT, camelot_distance, score_transition


def track(key, mode, bpm, energy):
    return {"id": "t", "name": "Test", "key": key, "mode": mode, "bpm": bpm, "energy": energy}


# ---------------------------------------------------------------------------
# CAMELOT dict sanity checks
# ---------------------------------------------------------------------------

class TestCamelotDict:
    def test_all_24_keys_present(self):
        assert len(CAMELOT) == 24

    def test_c_major_is_8b(self):
        assert CAMELOT[(0, 1)] == "8B"

    def test_a_minor_is_8a(self):
        # Relative minor of C major shares the same number
        assert CAMELOT[(9, 0)] == "8A"

    def test_b_major_is_1b(self):
        assert CAMELOT[(11, 1)] == "1B"


# ---------------------------------------------------------------------------
# camelot_distance
# ---------------------------------------------------------------------------

class TestCamelotDistance:
    def test_same_position_is_zero(self):
        assert camelot_distance("8B", "8B") == 0

    def test_adjacent_number_same_letter(self):
        assert camelot_distance("8B", "9B") == 1
        assert camelot_distance("8B", "7B") == 1

    def test_relative_major_minor_same_number(self):
        # 8B (C major) ↔ 8A (A minor)
        assert camelot_distance("8B", "8A") == 1

    def test_wrap_around_1_and_12(self):
        # 1B and 12B are adjacent on the wheel
        assert camelot_distance("1B", "12B") == 1

    def test_two_steps_away(self):
        # 8B → 10B skips one position
        assert camelot_distance("8B", "10B") == 2

    def test_opposite_side_of_wheel(self):
        # 8B and 2B are 6 positions apart (half the wheel)
        assert camelot_distance("8B", "2B") == 6

    def test_symmetry(self):
        assert camelot_distance("5A", "9A") == camelot_distance("9A", "5A")


# ---------------------------------------------------------------------------
# score_transition — key scenarios
# ---------------------------------------------------------------------------

class TestScoreTransition:
    def test_perfect_match(self):
        # Same key, BPM, and energy → all subscores 100
        a = track(0, 1, 128.0, 0.8)   # C major = 8B
        b = track(0, 1, 128.0, 0.8)
        result = score_transition(a, b)
        assert result["key_score"] == 100
        assert result["bpm_score"] == 100
        assert result["energy_score"] == 100
        assert result["score"] == 100.0
        assert result["energy_jump"] is False

    def test_adjacent_keys(self):
        # C major (8B) → G major (9B): adjacent on wheel
        a = track(0, 1, 128.0, 0.8)
        b = track(7, 1, 128.0, 0.8)
        result = score_transition(a, b)
        assert result["key_score"] == 85
        # 0.4*85 + 0.4*100 + 0.2*100 = 34 + 40 + 20 = 94
        assert result["score"] == 94.0

    def test_relative_major_minor(self):
        # C major (8B) → A minor (8A): same Camelot number
        a = track(0, 1, 128.0, 0.8)
        b = track(9, 0, 128.0, 0.8)
        result = score_transition(a, b)
        assert result["key_score"] == 75
        # 0.4*75 + 0.4*100 + 0.2*100 = 30 + 40 + 20 = 90
        assert result["score"] == 90.0

    def test_incompatible_keys(self):
        # C major (8B) → D major (10B): 2 positions apart
        a = track(0, 1, 128.0, 0.8)
        b = track(2, 1, 128.0, 0.8)
        result = score_transition(a, b)
        assert result["key_score"] == 40
        # 0.4*40 + 0.4*100 + 0.2*100 = 16 + 40 + 20 = 76
        assert result["score"] == 76.0

    def test_large_bpm_gap(self):
        # Same key, 15 BPM apart → bpm_score = 30
        a = track(0, 1, 128.0, 0.8)
        b = track(0, 1, 143.0, 0.8)
        result = score_transition(a, b)
        assert result["bpm_score"] == 30
        # 0.4*100 + 0.4*30 + 0.2*100 = 40 + 12 + 20 = 72
        assert result["score"] == 72.0

    def test_energy_jump_flagged(self):
        # Energy delta of 0.5 → score 40, energy_jump True
        a = track(0, 1, 128.0, 0.3)
        b = track(0, 1, 128.0, 0.8)
        result = score_transition(a, b)
        assert result["energy_score"] == 40
        assert result["energy_jump"] is True
        # 0.4*100 + 0.4*100 + 0.2*40 = 40 + 40 + 8 = 88
        assert result["score"] == 88.0

    def test_unknown_key_falls_back_to_40(self):
        # Spotify returns key=-1 when key detection fails
        a = track(-1, 1, 128.0, 0.8)
        b = track(0, 1, 128.0, 0.8)
        result = score_transition(a, b)
        assert result["key_score"] == 40

    def test_bpm_within_2_is_100(self):
        a = track(0, 1, 128.0, 0.8)
        b = track(0, 1, 129.5, 0.8)
        assert score_transition(a, b)["bpm_score"] == 100

    def test_energy_delta_just_below_0_2(self):
        a = track(0, 1, 128.0, 0.5)
        b = track(0, 1, 128.0, 0.69)  # delta ≈ 0.19 < 0.2
        result = score_transition(a, b)
        assert result["energy_score"] == 80
        assert result["energy_jump"] is False

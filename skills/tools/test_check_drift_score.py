"""Tests for check_drift_score.py — run with: python -m unittest test_check_drift_score"""

import unittest

from check_drift_score import (
    DIMENSIONS,
    ranked_gaps,
    tier,
    validate_raw,
    weighted,
    weighted_total,
)


class WeightContractTests(unittest.TestCase):
    def test_weights_sum_to_100(self):
        self.assertEqual(100, sum(w for _, _, w in DIMENSIONS))

    def test_d2_is_heaviest(self):
        weights = {dim_id: w for dim_id, _, w in DIMENSIONS}
        self.assertEqual(25, weights["D2"])
        self.assertEqual(weights["D2"], max(weights.values()))


class MathTests(unittest.TestCase):
    def test_perfect_vector_scores_100(self):
        self.assertEqual(100.0, weighted_total([4, 4, 4, 4, 4]))

    def test_zero_vector_scores_0(self):
        self.assertEqual(0.0, weighted_total([0, 0, 0, 0, 0]))

    def test_weighted_matches_formula(self):
        raws = [3, 2, 4, 1, 0]
        expected = [15 * 3 / 4.0, 25 * 2 / 4.0, 20 * 4 / 4.0, 20 * 1 / 4.0, 0.0]
        self.assertEqual(expected, weighted(raws))

    def test_skill_worked_example(self):
        # The example in check-agent-drift.md: raws 3,2,3,4,2 -> 68.75 Moderate.
        raws = [3, 2, 3, 4, 2]
        self.assertEqual(68.75, weighted_total(raws))
        name, total, clamped = tier(raws)
        self.assertEqual("Moderate Drift", name)
        self.assertFalse(clamped)


class TierBoundaryTests(unittest.TestCase):
    def assert_tier(self, raws, expected):
        name, _, _ = tier(raws)
        self.assertEqual(expected, name)

    def test_tier_lower_bounds(self):
        self.assert_tier([4, 4, 4, 4, 4], "Frontier-Aligned")   # 100
        self.assert_tier([4, 4, 4, 4, 1], "Frontier-Aligned")   # 85 exactly
        self.assert_tier([0, 4, 4, 4, 4], "Frontier-Aligned")   # 85 exactly
        self.assert_tier([0, 4, 4, 4, 3], "Minor Drift")        # 80
        self.assert_tier([0, 4, 4, 0, 3], "Moderate Drift")     # 60
        self.assert_tier([0, 4, 0, 0, 2], "High Drift")         # 35
        self.assert_tier([0, 4, 0, 0, 0], "Critical Drift")     # 25


class SafetyOverrideTests(unittest.TestCase):
    def test_d2_at_1_clamps_a_high_total(self):
        # 4,1,4,4,4 -> 81.25, base Minor Drift, must clamp to High Drift.
        name, total, clamped = tier([4, 1, 4, 4, 4])
        self.assertEqual(81.25, total)
        self.assertEqual("High Drift", name)
        self.assertTrue(clamped)

    def test_d2_at_0_clamps_too(self):
        name, _, clamped = tier([4, 0, 4, 4, 4])
        self.assertEqual("High Drift", name)
        self.assertTrue(clamped)

    def test_clamp_never_improves_a_worse_tier(self):
        # Total already Critical: clamp must not lift it to High Drift.
        name, total, clamped = tier([0, 0, 0, 0, 4])
        self.assertEqual(20.0, total)
        self.assertEqual("Critical Drift", name)
        self.assertFalse(clamped)

    def test_d2_at_2_does_not_clamp(self):
        name, _, clamped = tier([4, 2, 4, 4, 4])
        self.assertEqual("Frontier-Aligned", name)
        self.assertFalse(clamped)


class RankingTests(unittest.TestCase):
    def test_gaps_rank_by_weighted_gap_descending(self):
        # raws 3,2,3,4,2: gaps D1 3.75, D2 12.5, D3 5, D4 0, D5 10.
        order = [dim_id for dim_id, _, _ in ranked_gaps([3, 2, 3, 4, 2])]
        self.assertEqual(["D2", "D5", "D3", "D1", "D4"], order)

    def test_gap_values(self):
        gaps = {dim_id: gap for dim_id, _, gap in ranked_gaps([3, 2, 3, 4, 2])}
        self.assertEqual(12.5, gaps["D2"])
        self.assertEqual(10.0, gaps["D5"])
        self.assertEqual(0.0, gaps["D4"])


class ValidationTests(unittest.TestCase):
    def test_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            validate_raw([4, 4, 4, 4])

    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_raw([4, 4, 5, 4, 4])
        with self.assertRaises(ValueError):
            validate_raw([-1, 4, 4, 4, 4])

    def test_rejects_non_integers(self):
        with self.assertRaises(ValueError):
            validate_raw([4, 4, 3.5, 4, 4])
        with self.assertRaises(ValueError):
            validate_raw([True, 4, 4, 4, 4])


if __name__ == "__main__":
    unittest.main()

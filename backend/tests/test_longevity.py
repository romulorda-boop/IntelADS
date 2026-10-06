import unittest

from app.services.longevity import badge_for_score, calculate_longevity_score, score_breakdown


class LongevityScoreTests(unittest.TestCase):
    def test_score_uses_days_appearances_and_variations_then_caps_at_100(self) -> None:
        result = score_breakdown(active_days=45, appearances_last_30_days=10, variations_count=7)
        self.assertEqual(result["active_points"], 67.5)
        self.assertEqual(result["appearance_points"], 20)
        self.assertEqual(result["variation_points"], 20)
        self.assertEqual(result["score"], 100)
        self.assertEqual(calculate_longevity_score(45, 10, 7), 100)

    def test_frequency_and_variation_contributions_are_capped(self) -> None:
        self.assertEqual(calculate_longevity_score(0, 10, 7), 40)
        self.assertEqual(calculate_longevity_score(0, 30, 30), 40)

    def test_negative_inputs_are_treated_as_zero(self) -> None:
        self.assertEqual(calculate_longevity_score(-1, -10, -4), 0)

    def test_half_points_round_up_to_the_nearest_integer(self) -> None:
        self.assertEqual(calculate_longevity_score(1, 0, 0), 2)

    def test_badge_thresholds(self) -> None:
        self.assertEqual(badge_for_score(80), "Winner")
        self.assertEqual(badge_for_score(40), "Scaling")
        self.assertEqual(badge_for_score(39), "Testing")


if __name__ == "__main__":
    unittest.main()

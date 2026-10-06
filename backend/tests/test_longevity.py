from unittest import TestCase

from app.services.longevity import badge_for_score, calculate_longevity_score


class LongevityScoreTests(TestCase):
    def test_formula_and_cap(self) -> None:
        self.assertEqual(calculate_longevity_score(20, 2, 2, 5), 65)
        self.assertEqual(calculate_longevity_score(45, 4, 4, 20), 100)

    def test_badge_thresholds(self) -> None:
        self.assertEqual(badge_for_score(80), "Winner")
        self.assertEqual(badge_for_score(79), "Scaling")
        self.assertEqual(badge_for_score(40), "Scaling")
        self.assertEqual(badge_for_score(39), "Testing")

from __future__ import annotations

from datetime import datetime, timezone
from math import floor

FREQUENCY_WINDOW_DAYS = 30
APPEARANCE_POINTS_PER_EVENT = 2
MAX_APPEARANCE_POINTS = 20
VARIATION_POINTS_PER_AD = 3
MAX_VARIATION_POINTS = 20


def score_breakdown(
    active_days: int, appearances_last_30_days: int, variations_count: int
) -> dict[str, int | float]:
    """Break the approved 0–100 score into time, frequency and variation signals."""
    days = max(0, int(active_days))
    appearances = max(0, int(appearances_last_30_days))
    variations = max(0, int(variations_count))
    active_points = days * 1.5
    appearance_points = min(MAX_APPEARANCE_POINTS, appearances * APPEARANCE_POINTS_PER_EVENT)
    variation_points = min(MAX_VARIATION_POINTS, variations * VARIATION_POINTS_PER_AD)
    raw_score = active_points + appearance_points + variation_points
    score = min(100, floor(raw_score + 0.5))
    return {
        "active_days": days,
        "active_points": active_points,
        "appearances_last_30_days": appearances,
        "appearance_points": appearance_points,
        "variations_count": variations,
        "variation_points": variation_points,
        "score": score,
    }


def calculate_longevity_score(
    active_days: int, appearances_last_30_days: int, variations_count: int
) -> int:
    return int(score_breakdown(active_days, appearances_last_30_days, variations_count)["score"])


def badge_for_score(score: int) -> str:
    if score >= 80:
        return "Winner"
    if score >= 40:
        return "Scaling"
    return "Testing"


def active_days_between(first_seen_at: datetime, last_seen_at: datetime, is_active: bool) -> int:
    end = datetime.now(timezone.utc) if is_active else last_seen_at
    first = first_seen_at if first_seen_at.tzinfo else first_seen_at.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return max(0, (end - first).days)

from __future__ import annotations

from datetime import datetime, timezone


def calculate_longevity_score(
    active_days: int,
    num_networks: int,
    num_platforms: int,
    impression_bonus: float,
) -> int:
    """Apply the specification formula and persist its integer result."""
    raw_score = (
        (active_days * 1.5)
        + (num_networks * 10)
        + (num_platforms * 5)
        + impression_bonus
    )
    return min(100, int(round(raw_score)))


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

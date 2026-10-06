from __future__ import annotations

from uuid import UUID

from app.db.session import connect_db
from app.services.longevity import calculate_longevity_score
from app.services.phash import DEFAULT_HAMMING_THRESHOLD, MediaHashError, compute_ad_phash, find_similar_pairs


METRICS_SQL = """
    SELECT
        a.id,
        GREATEST(0, FLOOR(EXTRACT(EPOCH FROM
            ((CASE WHEN a.is_active THEN NOW() ELSE a.last_seen_at END) - a.first_seen_at)
        ) / 86400))::int AS active_days,
        (SELECT COUNT(*)::int FROM ad_appearances p
         WHERE p.ad_id = a.id
           AND p.observed_at >= NOW() - INTERVAL '30 days'
           AND p.observed_at <= NOW()) AS appearances_30d,
        (SELECT COUNT(*)::int FROM ad_variations v
         WHERE v.parent_ad_id = a.id OR v.variation_ad_id = a.id) AS variations_count
    FROM ads a
"""


def run_ad_analysis() -> dict[str, object]:
    """Generate pHashes, rebuild pair links and materialize the current longevity score."""
    errors: list[dict[str, str]] = []
    with connect_db() as conn:
        ads = conn.execute(
            "SELECT id, media_type, media_url, thumbnail_url FROM ads ORDER BY id"
        ).fetchall()
        hashes: dict[str, str] = {}
        ids_by_text: dict[str, UUID] = {}
        for ad in ads:
            ad_id = str(ad["id"])
            ids_by_text[ad_id] = ad["id"]
            try:
                hashes[ad_id] = compute_ad_phash(
                    ad["media_type"], ad["media_url"], ad["thumbnail_url"]
                )
            except MediaHashError as exc:
                errors.append({"ad_id": ad_id, "error": str(exc)[:200]})

        if errors:
            return {
                "ads_processed": len(ads),
                "hashes_generated": len(hashes),
                "similar_pairs": 0,
                "scores_updated": 0,
                "hamming_threshold": DEFAULT_HAMMING_THRESHOLD,
                "frequency_window_days": 30,
                "committed": False,
                "errors": errors,
            }

        for ad in ads:
            ad_id = str(ad["id"])
            conn.execute(
                "UPDATE ads SET phash = %s WHERE id = %s",
                (hashes.get(ad_id), ad["id"]),
            )

        # ad_variations stores derived, undirected canonical pairs; rebuild it from current hashes.
        conn.execute("DELETE FROM ad_variations")
        pairs = find_similar_pairs(hashes, DEFAULT_HAMMING_THRESHOLD)
        for left_id, right_id, distance in pairs:
            conn.execute(
                """
                INSERT INTO ad_variations (parent_ad_id, variation_ad_id, hamming_distance)
                VALUES (%s, %s, %s)
                ON CONFLICT (parent_ad_id, variation_ad_id)
                DO UPDATE SET hamming_distance = EXCLUDED.hamming_distance
                """,
                (ids_by_text[left_id], ids_by_text[right_id], distance),
            )

        metrics = conn.execute(METRICS_SQL).fetchall()
        for item in metrics:
            score = calculate_longevity_score(
                item["active_days"], item["appearances_30d"], item["variations_count"]
            )
            conn.execute("UPDATE ads SET longevity_score = %s WHERE id = %s", (score, item["id"]))

    return {
        "ads_processed": len(ads),
        "hashes_generated": len(hashes),
        "similar_pairs": len(pairs),
        "scores_updated": len(metrics),
        "hamming_threshold": DEFAULT_HAMMING_THRESHOLD,
        "frequency_window_days": 30,
        "committed": True,
        "errors": errors,
    }

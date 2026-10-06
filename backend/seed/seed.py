from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db.session import connect_db
from seed.fixtures import ADS, ADVERTISERS, APPS

MEDIA = {
    "game": ("/mock-media/gameplay.mp4", "/mock-media/gameplay.webp"),
    "beauty": ("/mock-media/beauty.mp4", "/mock-media/beauty-collection.jpg"),
    "fitness": ("/mock-media/fitness.mp4", "/mock-media/fitness-app.png"),
}


def _mock_appearances(active_days: int) -> int:
    # Simulated repeat sightings: a maximum of ten observations in a 30-day window.
    return max(1, min(10, (min(max(0, active_days), 30) + 2) // 3))


def run_seed() -> None:
    now = datetime.now(timezone.utc)
    if len(ADS) < 15 or len(ADS) > 20:
        raise ValueError("O seed deve conter entre 15 e 20 anúncios.")

    with connect_db() as conn:
        for advertiser in ADVERTISERS:
            conn.execute(
                """
                INSERT INTO advertisers (id, name, domain)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, domain = EXCLUDED.domain
                """,
                (advertiser["id"], advertiser["name"], advertiser["domain"]),
            )

        for app in APPS:
            conn.execute(
                """
                INSERT INTO apps (id, advertiser_id, platform, store_app_id, title,
                                  icon_url, downloads_count, rating, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    advertiser_id = EXCLUDED.advertiser_id,
                    title = CASE WHEN apps.sync_status = 'synced' THEN apps.title ELSE EXCLUDED.title END,
                    icon_url = CASE WHEN apps.sync_status = 'synced' THEN apps.icon_url ELSE EXCLUDED.icon_url END,
                    downloads_count = CASE WHEN apps.sync_status = 'synced' THEN apps.downloads_count ELSE EXCLUDED.downloads_count END,
                    rating = CASE WHEN apps.sync_status = 'synced' THEN apps.rating ELSE EXCLUDED.rating END,
                    category = CASE WHEN apps.sync_status = 'synced' THEN apps.category ELSE EXCLUDED.category END,
                    sync_status = CASE WHEN apps.sync_status = 'synced' THEN 'synced' ELSE 'mock' END,
                    last_synced_at = CASE WHEN apps.sync_status = 'synced' THEN apps.last_synced_at ELSE NULL END,
                    last_sync_error = CASE WHEN apps.sync_status = 'synced' THEN apps.last_sync_error ELSE NULL END
                """,
                (
                    app["id"],
                    ADVERTISERS[app["advertiser"] - 1]["id"],
                    app["platform"],
                    app["store_app_id"],
                    app["title"],
                    app["icon_url"],
                    app["downloads_count"],
                    app["rating"],
                    app["category"],
                ),
            )

        for ad in ADS:
            active_days = int(ad["days"])
            age_offset = 0 if ad["active"] else int(ad["stopped_days_ago"])
            last_seen = now - timedelta(days=age_offset)
            first_seen = last_seen - timedelta(days=active_days)
            media_url, thumbnail_url = MEDIA[ad["creative"]]
            app_id = APPS[ad["app"] - 1]["id"] if ad["app"] else None
            destination = f"https://example.com/mock-library/{ad['id'][-2:]}"
            conn.execute(
                """
                INSERT INTO ads (id, advertiser_id, app_id, title, caption_text, media_type,
                                 media_url, thumbnail_url, source_network, category, target_os,
                                 first_seen_at, last_seen_at, is_active, longevity_score, phash,
                                 destination_url)
                VALUES (%s, %s, %s, %s, %s, 'video', %s, %s, %s, %s,
                        %s::varchar(20)[], %s, %s, %s, 0, NULL, %s)
                ON CONFLICT (id) DO UPDATE SET
                    advertiser_id = EXCLUDED.advertiser_id,
                    app_id = EXCLUDED.app_id,
                    title = EXCLUDED.title,
                    caption_text = EXCLUDED.caption_text,
                    media_type = EXCLUDED.media_type,
                    media_url = EXCLUDED.media_url,
                    thumbnail_url = EXCLUDED.thumbnail_url,
                    source_network = EXCLUDED.source_network,
                    category = EXCLUDED.category,
                    target_os = EXCLUDED.target_os,
                    first_seen_at = EXCLUDED.first_seen_at,
                    last_seen_at = EXCLUDED.last_seen_at,
                    is_active = EXCLUDED.is_active,
                    destination_url = EXCLUDED.destination_url
                """,
                (
                    ad["id"],
                    ADVERTISERS[ad["advertiser"] - 1]["id"],
                    app_id,
                    ad["title"],
                    ad["caption"],
                    media_url,
                    thumbnail_url,
                    ad["network"],
                    ad["category"],
                    ad["target_os"],
                    first_seen,
                    last_seen,
                    ad["active"],
                    destination,
                ),
            )

        # Replace only the seed's own events; any future real observations are preserved.
        conn.execute("DELETE FROM ad_appearances WHERE is_mock IS TRUE")
        for ad in ADS:
            active_days = int(ad["days"])
            age_offset = 0 if ad["active"] else int(ad["stopped_days_ago"])
            last_seen = now - timedelta(days=age_offset)
            count = _mock_appearances(active_days)
            for index in range(count):
                offset = timedelta(days=30 * index / max(count, 1))
                conn.execute(
                    "INSERT INTO ad_appearances (ad_id, observed_at, is_mock) VALUES (%s, %s, TRUE)",
                    (ad["id"], last_seen - offset),
                )

    print(f"Seed concluído: {len(ADVERTISERS)} anunciantes, {len(APPS)} apps e {len(ADS)} anúncios.")
    print("Eventos de aparição simulados atualizados; relações e scores são gerados pelo worker pHash.")


if __name__ == "__main__":
    run_seed()

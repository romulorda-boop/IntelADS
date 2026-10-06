from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.db.session import connect_db
from app.services.longevity import calculate_longevity_score
from seed.fixtures import ADS, ADVERTISERS, APPS

MEDIA = {
    "game": ("/mock-media/gameplay.mp4", "/mock-media/gameplay.webp"),
    "beauty": ("/mock-media/beauty.mp4", "/mock-media/beauty-collection.jpg"),
    "fitness": ("/mock-media/fitness.mp4", "/mock-media/fitness-app.png"),
}


def run_seed() -> None:
    now = datetime.now(timezone.utc)
    networks_by_hash: dict[str, set[str]] = defaultdict(set)
    for ad in ADS:
        networks_by_hash[ad["phash"]].add(ad["network"])

    app_ids = {app["id"] for app in APPS}
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
            active_days = ad["days"]
            score = calculate_longevity_score(
                active_days=active_days,
                num_networks=len(networks_by_hash[ad["phash"]]),
                num_platforms=ad["meta_platforms"],
                impression_bonus=ad["impression_bonus"],
            )
            age_offset = 0 if ad["active"] else ad["stopped_days_ago"]
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
                        %s::varchar(20)[], %s, %s, %s, %s, %s, %s)
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
                    longevity_score = EXCLUDED.longevity_score,
                    phash = EXCLUDED.phash,
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
                    score,
                    ad["phash"],
                    destination,
                ),
            )

        for group in ("a100000000000001", "a100000000000002", "a100000000000003", "a100000000000005", "a100000000000008"):
            members = [ad for ad in ADS if ad["phash"] == group]
            if len(members) > 1:
                parent = members[0]["id"]
                for variation in members[1:]:
                    conn.execute(
                        """
                        INSERT INTO ad_variations (parent_ad_id, variation_ad_id, hamming_distance)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (parent_ad_id, variation_ad_id)
                        DO UPDATE SET hamming_distance = EXCLUDED.hamming_distance
                        """,
                        (parent, variation["id"], 4),
                    )

    print(f"Seed concluído: {len(ADVERTISERS)} anunciantes, {len(APPS)} apps e {len(ADS)} anúncios.")
    print(f"Apps vinculados no seed: {len(app_ids)} IDs estáveis.")


if __name__ == "__main__":
    run_seed()

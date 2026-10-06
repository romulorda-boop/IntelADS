from __future__ import annotations

from math import ceil
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.db.session import connect_db
from app.schemas.ads import AdSearchRequest
from app.services.longevity import badge_for_score

router = APIRouter(tags=["ads"])

SORTS = {
    "longevity_score_desc": "a.longevity_score DESC, a.first_seen_at DESC",
    "first_seen_desc": "a.first_seen_at DESC",
    "active_days_desc": "active_days DESC, a.longevity_score DESC",
}

FROM_SQL = """
    FROM ads a
    LEFT JOIN advertisers advertiser ON advertiser.id = a.advertiser_id
    LEFT JOIN apps app ON app.id = a.app_id
"""


@router.post("/ads/search")
def search_ads(payload: AdSearchRequest) -> dict:
    where: list[str] = []
    params: list[object] = []

    if payload.query and payload.query.strip():
        term = f"%{payload.query.strip()}%"
        where.append(
            "(COALESCE(a.title, '') ILIKE %s OR COALESCE(a.caption_text, '') ILIKE %s "
            "OR COALESCE(advertiser.name, '') ILIKE %s OR COALESCE(app.title, '') ILIKE %s)"
        )
        params.extend([term, term, term, term])
    if payload.category:
        where.append("a.category = %s")
        params.append(payload.category)
    if payload.target_os:
        where.append("a.target_os && %s::varchar(20)[]")
        params.append(payload.target_os)
    if payload.networks:
        where.append("a.source_network = ANY(%s::varchar(30)[])")
        params.append(payload.networks)
    if payload.min_longevity_score is not None:
        where.append("a.longevity_score >= %s")
        params.append(payload.min_longevity_score)
    if payload.max_longevity_score is not None:
        where.append("a.longevity_score <= %s")
        params.append(payload.max_longevity_score)
    if payload.is_active_only:
        where.append("a.is_active IS TRUE")
    if payload.advertiser_id:
        try:
            advertiser_uuid = UUID(payload.advertiser_id)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="advertiser_id deve ser um UUID válido") from exc
        where.append("a.advertiser_id = %s")
        params.append(advertiser_uuid)

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    order_sql = SORTS[payload.sort_by]
    active_days_sql = "GREATEST(0, FLOOR(EXTRACT(EPOCH FROM ((CASE WHEN a.is_active THEN NOW() ELSE a.last_seen_at END) - a.first_seen_at)) / 86400))::int"

    with connect_db() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS total {FROM_SQL} {where_sql}", params
        ).fetchone()["total"]
        offset = (payload.page - 1) * payload.limit
        rows = conn.execute(
            f"""
            SELECT
                a.id, a.title, a.caption_text AS caption, a.media_type, a.media_url,
                a.thumbnail_url, a.source_network, a.category, a.target_os,
                a.first_seen_at, a.last_seen_at, a.is_active, a.longevity_score,
                a.destination_url,
                {active_days_sql} AS active_days,
                (SELECT COUNT(*) FROM ad_variations v
                 WHERE v.parent_ad_id = a.id OR v.variation_ad_id = a.id) AS variations_count,
                advertiser.id AS advertiser_id, advertiser.name AS advertiser_name,
                app.id AS app_id, app.store_app_id, app.title AS app_title,
                app.platform AS app_platform, app.downloads_count, app.rating AS app_rating,
                app.icon_url AS app_icon_url, app.sync_status AS app_sync_status,
                app.last_synced_at AS app_last_synced_at
            {FROM_SQL}
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
            """,
            [*params, payload.limit, offset],
        ).fetchall()

    results = []
    for row in rows:
        app = None
        if row["app_title"]:
            app = {
                "id": str(row["app_id"]),
                "store_app_id": row["store_app_id"],
                "title": row["app_title"],
                "platform": row["app_platform"],
                "downloads_count": row["downloads_count"],
                "rating": float(row["app_rating"]) if row["app_rating"] is not None else None,
                "icon_url": row["app_icon_url"],
                "sync_status": row["app_sync_status"] or "mock",
                "last_synced_at": row["app_last_synced_at"].isoformat() if row["app_last_synced_at"] else None,
            }
        advertiser = None
        if row["advertiser_id"]:
            advertiser = {"id": str(row["advertiser_id"]), "name": row["advertiser_name"]}
        score = row["longevity_score"] or 0
        results.append(
            {
                "id": str(row["id"]),
                "title": row["title"],
                "caption": row["caption"],
                "media_type": row["media_type"],
                "media_url": row["media_url"],
                "thumbnail_url": row["thumbnail_url"],
                "source_network": row["source_network"],
                "category": row["category"],
                "target_os": row["target_os"],
                "longevity_score": score,
                "badge": badge_for_score(score),
                "active_days": row["active_days"],
                "first_seen_at": row["first_seen_at"].isoformat(),
                "is_active": row["is_active"],
                "variations_count": row["variations_count"],
                "destination_url": row["destination_url"],
                "advertiser": advertiser,
                "app": app,
            }
        )

    return {
        "total": total,
        "page": payload.page,
        "total_pages": ceil(total / payload.limit) if total else 0,
        "results": results,
    }

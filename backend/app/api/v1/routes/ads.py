from __future__ import annotations

from math import ceil
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.db.session import connect_db
from app.schemas.ads_response import AdResponse, AdSearchResponse, SimilarAdsResponse
from app.schemas.ads import AdSearchRequest
from app.services.longevity import FREQUENCY_WINDOW_DAYS, badge_for_score, score_breakdown

router = APIRouter(tags=["ads"])

SCORE_CTE = f"""
WITH ad_metrics AS (
    SELECT
        a.id,
        GREATEST(0, FLOOR(EXTRACT(EPOCH FROM
            ((CASE WHEN a.is_active THEN NOW() ELSE a.last_seen_at END) - a.first_seen_at)
        ) / 86400))::int AS active_days,
        COALESCE(s.appearances_30d, 0)::int AS appearances_30d,
        COALESCE(v.variations_count, 0)::int AS variations_count
    FROM ads a
    LEFT JOIN LATERAL (
        SELECT COUNT(*)::int AS appearances_30d
        FROM ad_appearances seen
        WHERE seen.ad_id = a.id
          AND seen.observed_at >= NOW() - INTERVAL '{FREQUENCY_WINDOW_DAYS} days'
          AND seen.observed_at <= NOW()
    ) s ON TRUE
    LEFT JOIN LATERAL (
        SELECT COUNT(*)::int AS variations_count
        FROM ad_variations variation
        WHERE variation.parent_ad_id = a.id OR variation.variation_ad_id = a.id
    ) v ON TRUE
), scored AS (
    SELECT
        ad_metrics.*,
        LEAST(100, FLOOR(
            active_days * 1.5
            + LEAST(20, appearances_30d * 2)
            + LEAST(20, variations_count * 3)
            + 0.5
        ))::int AS longevity_score
    FROM ad_metrics
)
"""

SORTS = {
    "longevity_score_desc": "m.longevity_score DESC, a.first_seen_at DESC",
    "first_seen_desc": "a.first_seen_at DESC",
    "active_days_desc": "m.active_days DESC, m.longevity_score DESC",
}

FROM_SQL = """
    FROM scored m
    JOIN ads a ON a.id = m.id
    LEFT JOIN advertisers advertiser ON advertiser.id = a.advertiser_id
    LEFT JOIN apps app ON app.id = a.app_id
"""

SELECT_SQL = """
    SELECT
        a.id, a.title, a.caption_text AS caption, a.media_type, a.media_url,
        a.thumbnail_url, a.source_network, a.category, a.target_os,
        a.first_seen_at, a.last_seen_at, a.is_active, a.destination_url,
        m.longevity_score, m.active_days, m.appearances_30d, m.variations_count,
        advertiser.id AS advertiser_id, advertiser.name AS advertiser_name,
        app.id AS app_id, app.store_app_id, app.title AS app_title,
        app.platform AS app_platform, app.downloads_count, app.rating AS app_rating,
        app.icon_url AS app_icon_url, app.category AS app_category,
        app.sync_status AS app_sync_status,
        app.last_synced_at AS app_last_synced_at,
        COALESCE((
            SELECT json_agg(
                json_build_object(
                    'id', variant.id::text,
                    'title', variant.title,
                    'source_network', variant.source_network,
                    'thumbnail_url', variant.thumbnail_url,
                    'hamming_distance', variant.hamming_distance
                ) ORDER BY variant.hamming_distance, variant.title
            )
            FROM (
                SELECT
                    other.id, other.title, other.source_network, other.thumbnail_url,
                    link.hamming_distance
                FROM ad_variations link
                JOIN ads other ON other.id = CASE
                    WHEN link.parent_ad_id = a.id THEN link.variation_ad_id
                    ELSE link.parent_ad_id
                END
                WHERE link.parent_ad_id = a.id OR link.variation_ad_id = a.id
            ) AS variant
        ), '[]'::json) AS variants
"""


def _serialize_ad(row: dict) -> dict:
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
            "category": row["app_category"],
            "sync_status": row["app_sync_status"] or "mock",
            "last_synced_at": row["app_last_synced_at"].isoformat() if row["app_last_synced_at"] else None,
        }
    advertiser = None
    if row["advertiser_id"]:
        advertiser = {"id": str(row["advertiser_id"]), "name": row["advertiser_name"]}
    score = int(row["longevity_score"] or 0)
    variants = row["variants"] or []
    return {
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
        "score_breakdown": score_breakdown(
            row["active_days"], row["appearances_30d"], row["variations_count"]
        ),
        "active_days": row["active_days"],
        "first_seen_at": row["first_seen_at"].isoformat(),
        "is_active": row["is_active"],
        "variations_count": row["variations_count"],
        "variants": variants,
        "destination_url": row["destination_url"],
        "advertiser": advertiser,
        "app": app,
    }


def _select_where(where_sql: str, params: list[object], limit: int | None = None, offset: int = 0) -> list[dict]:
    pagination = ""
    full_params = list(params)
    if limit is not None:
        pagination = " LIMIT %s OFFSET %s"
        full_params.extend([limit, offset])
    with connect_db() as conn:
        return conn.execute(
            f"{SCORE_CTE}{SELECT_SQL}{FROM_SQL} {where_sql} ORDER BY a.id{pagination}",
            full_params,
        ).fetchall()


@router.post("/ads/search", response_model=AdSearchResponse)
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
        where.append("m.longevity_score >= %s")
        params.append(payload.min_longevity_score)
    if payload.max_longevity_score is not None:
        where.append("m.longevity_score <= %s")
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
    offset = (payload.page - 1) * payload.limit
    with connect_db() as conn:
        total = conn.execute(
            f"{SCORE_CTE} SELECT COUNT(*) AS total {FROM_SQL} {where_sql}", params
        ).fetchone()["total"]
        rows = conn.execute(
            f"{SCORE_CTE}{SELECT_SQL}{FROM_SQL} {where_sql} ORDER BY {order_sql} LIMIT %s OFFSET %s",
            [*params, payload.limit, offset],
        ).fetchall()
    return {
        "total": total,
        "page": payload.page,
        "total_pages": ceil(total / payload.limit) if total else 0,
        "results": [_serialize_ad(row) for row in rows],
    }


@router.get("/ads/{ad_id}/similars", response_model=SimilarAdsResponse)
def get_similar_ads(ad_id: UUID) -> dict:
    with connect_db() as conn:
        exists = conn.execute("SELECT 1 FROM ads WHERE id = %s", (ad_id,)).fetchone()
    if not exists:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado.")
    row = _select_where("WHERE a.id = %s", [ad_id])[0]
    ad = _serialize_ad(row)
    return {
        "ad_id": str(ad_id),
        "hamming_threshold": 10,
        "longevity_score": ad["longevity_score"],
        "badge": ad["badge"],
        "score_breakdown": ad["score_breakdown"],
        "results": ad["variants"],
    }


@router.get("/ads/{ad_id}", response_model=AdResponse)
def get_ad_details(ad_id: UUID) -> dict:
    rows = _select_where("WHERE a.id = %s", [ad_id])
    if not rows:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado.")
    return _serialize_ad(rows[0])

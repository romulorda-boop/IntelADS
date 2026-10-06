from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.db.session import connect_db

router = APIRouter(tags=["advertisers"])


def _percentages(rows: list[dict], keys: tuple[str, ...], label: str) -> dict[str, float]:
    counts = {row[label]: row["amount"] for row in rows}
    total = sum(counts.values())
    result = {key: round((counts.get(key, 0) / total) * 100, 1) if total else 0.0 for key in keys}
    present = [key for key in keys if counts.get(key, 0)]
    if total and present:
        last = present[-1]
        result[last] = round(result[last] + 100.0 - sum(result.values()), 1)
    return result


@router.get("/advertisers/{advertiser_id}")
def get_advertiser(advertiser_id: str) -> dict:
    try:
        advertiser_uuid = UUID(advertiser_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Anunciante não encontrado") from exc

    with connect_db() as conn:
        advertiser = conn.execute(
            "SELECT id, name, domain FROM advertisers WHERE id = %s",
            (advertiser_uuid,),
        ).fetchone()
        if advertiser is None:
            raise HTTPException(status_code=404, detail="Anunciante não encontrado")

        totals = conn.execute(
            """
            SELECT COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE is_active IS TRUE) AS active,
                   COUNT(*) FILTER (WHERE is_active IS FALSE) AS inactive
            FROM ads WHERE advertiser_id = %s
            """,
            (advertiser_uuid,),
        ).fetchone()
        os_rows = conn.execute(
            """
            SELECT target.os AS key, COUNT(*) AS amount
            FROM ads a CROSS JOIN LATERAL unnest(a.target_os) AS target(os)
            WHERE a.advertiser_id = %s
            GROUP BY target.os
            """,
            (advertiser_uuid,),
        ).fetchall()
        network_rows = conn.execute(
            """
            SELECT source_network AS key, COUNT(*) AS amount
            FROM ads WHERE advertiser_id = %s
            GROUP BY source_network
            """,
            (advertiser_uuid,),
        ).fetchall()
        apps = conn.execute(
            """
            SELECT title, store_app_id AS store_id, downloads_count AS downloads, platform
            FROM apps WHERE advertiser_id = %s ORDER BY title, platform
            """,
            (advertiser_uuid,),
        ).fetchall()

    return {
        "advertiser_id": str(advertiser["id"]),
        "name": advertiser["name"],
        "domain": advertiser["domain"],
        "total_ads_captured": totals["total"],
        "active_ads": totals["active"],
        "inactive_ads": totals["inactive"],
        "os_distribution": _percentages(os_rows, ("android", "ios", "desktop"), "key"),
        "network_distribution": _percentages(network_rows, ("meta", "google", "tiktok", "kwai"), "key"),
        "apps_linked": [dict(app) for app in apps],
    }

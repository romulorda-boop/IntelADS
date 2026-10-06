from __future__ import annotations

from uuid import UUID

from app.db.session import connect_db
from app.services.stores.apple_app_store import fetch_app_store_metadata
from app.services.stores.common import StoreLookupError
from app.services.stores.google_play import fetch_google_play_metadata


class AppNotFoundError(Exception):
    pass


class AppSyncError(Exception):
    def __init__(self, public_message: str, code: str = "sync_failed") -> None:
        super().__init__(public_message)
        self.public_message = public_message
        self.code = code


def _resolve_app(reference: str) -> dict | None:
    try:
        app_uuid = UUID(reference)
    except ValueError:
        app_uuid = None

    with connect_db() as conn:
        if app_uuid is not None:
            return conn.execute(
                "SELECT id, platform, store_app_id FROM apps WHERE id = %s",
                (app_uuid,),
            ).fetchone()
        return conn.execute(
            "SELECT id, platform, store_app_id FROM apps WHERE store_app_id = %s",
            (reference,),
        ).fetchone()


def _set_sync_error(app_id: UUID, code: str) -> None:
    with connect_db() as conn:
        conn.execute(
            "UPDATE apps SET sync_status = 'error', last_sync_error = %s WHERE id = %s",
            (code, app_id),
        )


def sync_app(reference: str) -> dict:
    """Synchronize one pre-registered app by database UUID or store identifier."""
    row = _resolve_app(reference)
    if row is None:
        raise AppNotFoundError("Aplicativo não encontrado no PostgreSQL.")

    app_uuid = row["id"]
    platform = row["platform"]
    store_app_id = row["store_app_id"]
    with connect_db() as conn:
        conn.execute(
            "UPDATE apps SET sync_status = 'syncing', last_sync_error = NULL WHERE id = %s",
            (app_uuid,),
        )

    try:
        if platform == "android":
            metadata = fetch_google_play_metadata(store_app_id)
        elif platform == "ios":
            metadata = fetch_app_store_metadata(store_app_id)
        else:
            raise StoreLookupError("Plataforma de loja não suportada.", "unsupported_platform")
    except StoreLookupError as exc:
        _set_sync_error(app_uuid, exc.code)
        raise AppSyncError(exc.public_message, exc.code) from exc
    except Exception as exc:
        _set_sync_error(app_uuid, "sync_failed")
        raise AppSyncError(
            "Não foi possível concluir a sincronização com a loja. Tente novamente mais tarde.",
            "sync_failed",
        ) from exc

    with connect_db() as conn:
        updated = conn.execute(
            """
            UPDATE apps
            SET title = %s,
                downloads_count = %s,
                rating = %s,
                icon_url = COALESCE(%s, icon_url),
                category = COALESCE(%s, category),
                last_synced_at = CURRENT_TIMESTAMP,
                sync_status = 'synced',
                last_sync_error = NULL
            WHERE id = %s
            RETURNING id, advertiser_id, platform, store_app_id, title, downloads_count,
                      rating, icon_url, category, sync_status, last_synced_at
            """,
            (
                metadata.title,
                metadata.downloads_count,
                metadata.rating,
                metadata.icon_url,
                metadata.category,
                app_uuid,
            ),
        ).fetchone()

    return {
        "id": str(updated["id"]),
        "advertiser_id": str(updated["advertiser_id"]) if updated["advertiser_id"] else None,
        "platform": updated["platform"],
        "store_app_id": updated["store_app_id"],
        "title": updated["title"],
        "downloads_count": updated["downloads_count"],
        "rating": float(updated["rating"]) if updated["rating"] is not None else None,
        "icon_url": updated["icon_url"],
        "category": updated["category"],
        "sync_status": updated["sync_status"],
        "last_synced_at": updated["last_synced_at"].isoformat(),
    }

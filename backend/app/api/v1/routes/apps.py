from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path

from app.services.app_sync import AppNotFoundError, AppSyncError, sync_app

router = APIRouter(tags=["apps"])


@router.post("/apps/sync/{app_id}")
def sync_app_endpoint(app_id: str = Path(min_length=1, max_length=255)) -> dict:
    try:
        return sync_app(app_id)
    except AppNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AppSyncError as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": exc.code, "message": exc.public_message},
        ) from exc

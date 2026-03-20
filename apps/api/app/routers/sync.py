"""Data sync / ingestion endpoints for pulling data from source systems."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/full")
async def run_full_sync(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "analyst")),
):
    svc = SyncService(db)
    result = await svc.run_full_sync()
    return result


@router.post("/users")
async def sync_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "analyst")),
):
    svc = SyncService(db)
    return await svc.sync_users()


@router.post("/groups")
async def sync_groups(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "analyst")),
):
    svc = SyncService(db)
    return await svc.sync_groups()


@router.post("/entitlements")
async def sync_entitlements(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "analyst")),
):
    svc = SyncService(db)
    return await svc.sync_entitlements()

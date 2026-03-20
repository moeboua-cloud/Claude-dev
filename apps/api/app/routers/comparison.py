"""Access comparison / variance analysis endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.comparison_service import ComparisonService
from app.schemas.comparison import AccessComparisonResponse

router = APIRouter(prefix="/comparison", tags=["comparison"])


@router.get("/{user_id}", response_model=AccessComparisonResponse)
async def compare_user_access(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = ComparisonService(db)
    result = await svc.compare_user_access(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found or comparison failed")
    return result

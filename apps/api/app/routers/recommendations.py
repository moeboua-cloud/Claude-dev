"""Recommendation endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.engine.recommendation_engine import RecommendationEngine
from app.schemas.recommendation import RecommendationResponse, RecommendationListResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationListResponse)
async def list_recommendations(
    status: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    engine = RecommendationEngine(db)
    recs, total = await engine.get_pending_recommendations(limit, offset)
    return RecommendationListResponse(
        items=[RecommendationResponse.model_validate(r) for r in recs],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/{user_id}/generate", response_model=list[RecommendationResponse])
async def generate_recommendations(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    engine = RecommendationEngine(db)
    recs = await engine.generate_recommendations(user_id)
    return [RecommendationResponse.model_validate(r) for r in recs]

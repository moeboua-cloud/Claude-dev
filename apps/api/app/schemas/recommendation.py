"""Schemas for recommendations."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    id: UUID
    user_id: UUID
    user_display_name: str | None = None
    recommendation_type: str
    category: str
    title: str
    description: str
    evidence: dict
    risk_level: str
    confidence_score: float
    status: str
    requires_approval: bool
    suggested_action: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationListResponse(BaseModel):
    items: list[RecommendationResponse]
    total: int
    offset: int
    limit: int

"""Schemas for audit logs."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    correlation_id: str
    event_type: str
    actor: str
    actor_role: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    summary: str
    details: Optional[dict] = None
    evidence_sources: Optional[list] = None
    policy_results: Optional[list] = None
    risk_level: Optional[str] = None
    outcome: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    offset: int
    limit: int


class AuditTimelineResponse(BaseModel):
    correlation_id: str
    events: list[AuditLogResponse]
    summary: str

"""Audit log endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.audit_service import AuditService
from app.schemas.audit import AuditLogResponse, AuditLogListResponse, AuditTimelineResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    event_type: str | None = Query(None),
    target_id: str | None = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = AuditService(db)
    logs, total = await svc.get_logs(event_type, target_id, limit, offset)
    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(l) for l in logs],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/timeline/{correlation_id}", response_model=AuditTimelineResponse)
async def get_audit_timeline(
    correlation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = AuditService(db)
    events = await svc.get_timeline(correlation_id)
    summary = f"Timeline with {len(events)} events for correlation {correlation_id}"
    return AuditTimelineResponse(
        correlation_id=correlation_id,
        events=[AuditLogResponse.model_validate(e) for e in events],
        summary=summary,
    )

"""Audit service - comprehensive logging for all platform activity."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.core.correlation import get_correlation_id


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        event_type: str,
        actor: str,
        summary: str,
        actor_role: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        details: dict | None = None,
        evidence_sources: list | None = None,
        policy_results: list | None = None,
        risk_level: str | None = None,
        outcome: str | None = None,
    ) -> AuditLog:
        correlation_id = get_correlation_id()
        entry = AuditLog(
            correlation_id=correlation_id,
            event_type=event_type,
            actor=actor,
            actor_role=actor_role,
            target_type=target_type,
            target_id=target_id,
            summary=summary,
            details=details,
            evidence_sources=evidence_sources,
            policy_results=policy_results,
            risk_level=risk_level,
            outcome=outcome,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def get_timeline(self, correlation_id: str) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.correlation_id == correlation_id)
            .order_by(AuditLog.timestamp)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_logs(
        self,
        event_type: str | None = None,
        target_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[AuditLog], int]:
        stmt = select(AuditLog)
        if event_type:
            stmt = stmt.where(AuditLog.event_type == event_type)
        if target_id:
            stmt = stmt.where(AuditLog.target_id == target_id)

        count_stmt = select(AuditLog.id)
        if event_type:
            count_stmt = count_stmt.where(AuditLog.event_type == event_type)
        if target_id:
            count_stmt = count_stmt.where(AuditLog.target_id == target_id)
        count_result = await self.db.execute(count_stmt)
        total = len(count_result.all())

        stmt = stmt.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

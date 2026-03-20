"""Audit log model - the single source of truth for all platform activity."""

import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    # query, policy_eval, recommendation, approval, action, sync, error
    actor: Mapped[str] = mapped_column(String(100))
    actor_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # user, entitlement, group
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    summary: Mapped[str] = mapped_column(Text)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evidence_sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    policy_results: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)

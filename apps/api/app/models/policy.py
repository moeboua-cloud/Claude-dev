"""Policy rule and evaluation models."""

import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, Text, DateTime, Boolean, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PolicyRule(Base):
    """Deterministic policy rules for action gating."""

    __tablename__ = "policy_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rule_type: Mapped[str] = mapped_column(String(50))  # action_gate, sod, risk_threshold, approval_required
    conditions: Mapped[dict] = mapped_column(JSON)
    actions: Mapped[dict] = mapped_column(JSON)  # {"require_approval": true, "approvers": ["manager", "app_owner"]}
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")
    priority: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    environment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # None = all environments
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class PolicyEvaluation(Base):
    """Record of a policy evaluation against a proposed action."""

    __tablename__ = "policy_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
    policy_rule_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    policy_rule_name: Mapped[str] = mapped_column(String(200))
    input_context: Mapped[dict] = mapped_column(JSON)
    result: Mapped[str] = mapped_column(String(20))  # allow, deny, require_approval
    reason: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(20))
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

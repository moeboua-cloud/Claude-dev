"""Approval workflow models."""

import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
    recommendation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recommendations.id"))
    requested_by: Mapped[str] = mapped_column(String(100))
    target_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action_type: Mapped[str] = mapped_column(String(50))
    action_details: Mapped[dict] = mapped_column(JSON)
    risk_level: Mapped[str] = mapped_column(String(20))
    required_approvers: Mapped[list] = mapped_column(JSON)  # ["manager", "app_owner"]
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected, expired
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    approval_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("approval_requests.id"))
    approver_id: Mapped[str] = mapped_column(String(100))
    approver_role: Mapped[str] = mapped_column(String(50))  # manager, app_owner, iam_admin
    decision: Mapped[str] = mapped_column(String(20))  # approved, rejected
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

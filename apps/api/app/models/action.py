"""Action execution record models."""

import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ActionRecord(Base):
    __tablename__ = "action_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
    approval_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_requests.id"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(String(50))  # add_group, remove_group, grant_app, revoke_app
    target_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    target_entitlement_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entitlements.id"), nullable=True
    )
    execution_mode: Mapped[str] = mapped_column(String(20))  # simulation, execution
    input_payload: Mapped[dict] = mapped_column(JSON)
    result: Mapped[str] = mapped_column(String(20))  # success, failure, simulated
    result_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    rollback_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    executed_by: Mapped[str] = mapped_column(String(100))
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

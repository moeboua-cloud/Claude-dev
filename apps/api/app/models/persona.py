"""Persona and baseline access models."""

import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Persona(Base):
    """Represents a role-based persona with expected baseline access."""

    __tablename__ = "personas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_family: Mapped[str] = mapped_column(String(100), index=True)
    sub_job_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    worker_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    entitlements: Mapped[list["PersonaEntitlement"]] = relationship(back_populates="persona", cascade="all, delete-orphan")
    mapping_rules: Mapped[list["PersonaMappingRule"]] = relationship(back_populates="persona", cascade="all, delete-orphan")


class PersonaMappingRule(Base):
    """Rules that map user attributes to personas."""

    __tablename__ = "persona_mapping_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    persona_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("personas.id"))
    priority: Mapped[int] = mapped_column(Integer, default=100)
    conditions: Mapped[dict] = mapped_column(JSON)  # {"job_family": "Finance", "region": "US"}
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    persona: Mapped["Persona"] = relationship(back_populates="mapping_rules")


class PersonaEntitlement(Base):
    """Expected baseline entitlements for a persona."""

    __tablename__ = "persona_entitlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    persona_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("personas.id"))
    entitlement_type: Mapped[str] = mapped_column(String(50))  # group, app_role, license
    entitlement_identifier: Mapped[str] = mapped_column(String(255))  # group DN, app ID, etc.
    entitlement_name: Mapped[str] = mapped_column(String(255))
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    is_privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")  # low, medium, high, critical
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approval_chain: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    persona: Mapped["Persona"] = relationship(back_populates="entitlements")

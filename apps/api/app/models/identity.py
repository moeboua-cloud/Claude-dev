"""Identity / user models."""

import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, Text, DateTime, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

import enum


class LifecycleState(str, enum.Enum):
    PRE_HIRE = "pre_hire"
    ACTIVE = "active"
    MOVER = "mover"
    LEAVER = "leaver"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"


class WorkerType(str, enum.Enum):
    EMPLOYEE = "employee"
    CONTRACTOR = "contractor"
    VENDOR = "vendor"
    SERVICE_ACCOUNT = "service_account"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    upn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sam_account_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # HR attributes
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    job_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sub_job_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cost_center: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    legal_entity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    manager_employee_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    worker_type: Mapped[WorkerType] = mapped_column(SAEnum(WorkerType), default=WorkerType.EMPLOYEE)
    lifecycle_state: Mapped[LifecycleState] = mapped_column(SAEnum(LifecycleState), default=LifecycleState.ACTIVE)

    # Timestamps
    hire_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    termination_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    attributes: Mapped[list["UserAttribute"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    entitlements: Mapped[list["UserEntitlement"]] = relationship(  # type: ignore[name-defined]
        back_populates="user", cascade="all, delete-orphan"
    )
    lifecycle_events: Mapped[list["UserLifecycleEvent"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserAttribute(Base):
    """Flexible key-value attributes from source systems."""

    __tablename__ = "user_attributes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    source: Mapped[str] = mapped_column(String(50))  # workday, ad, entra
    attribute_name: Mapped[str] = mapped_column(String(100))
    attribute_value: Mapped[str] = mapped_column(Text)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship(back_populates="attributes")


class UserLifecycleEvent(Base):
    """Tracks lifecycle transitions (join, move, leave)."""

    __tablename__ = "user_lifecycle_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(50))  # join, move, leave, rehire
    previous_state: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    new_state: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    effective_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    processed: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="lifecycle_events")

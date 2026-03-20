"""Entitlement, application, and group models."""

import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    app_type: Mapped[str] = mapped_column(String(50))  # saas, on_prem, hybrid
    owner_employee_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    owner_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    criticality: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, critical
    requires_license: Mapped[bool] = mapped_column(Boolean, default=False)
    sso_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    provisioning_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # scim, manual, ad_group
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    group_type: Mapped[str] = mapped_column(String(50))  # security, distribution, m365, role
    source: Mapped[str] = mapped_column(String(50))  # ad, entra, app
    is_privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    owner_employee_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Entitlement(Base):
    """Normalized entitlement catalog entry."""

    __tablename__ = "entitlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True)
    entitlement_type: Mapped[str] = mapped_column(String(50))  # group_membership, app_role, license, permission, file_share
    source_system: Mapped[str] = mapped_column(String(50))
    source_identifier: Mapped[str] = mapped_column(String(500))
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=True)
    group_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)
    is_privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # privileged_access, license, distribution_list, security_group, app_role, file_share
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class UserEntitlement(Base):
    """Actual entitlements assigned to a user."""

    __tablename__ = "user_entitlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    entitlement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entitlements.id"))
    source: Mapped[str] = mapped_column(String(50))  # ad, entra, app, manual
    granted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    granted_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_direct: Mapped[bool] = mapped_column(Boolean, default=True)  # vs inherited/nested
    is_exception: Mapped[bool] = mapped_column(Boolean, default=False)
    exception_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exception_approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_review_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship(back_populates="entitlements")  # type: ignore[name-defined]
    entitlement: Mapped["Entitlement"] = relationship()

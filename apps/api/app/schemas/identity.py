"""Pydantic schemas for identity / user data."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    employee_id: str
    email: str
    display_name: str
    first_name: str
    last_name: str
    job_title: Optional[str] = None
    job_family: Optional[str] = None
    sub_job_family: Optional[str] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    legal_entity: Optional[str] = None
    region: Optional[str] = None
    location: Optional[str] = None
    manager_employee_id: Optional[str] = None
    worker_type: str = "employee"
    lifecycle_state: str = "active"


class UserResponse(UserBase):
    id: UUID
    hire_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserDetailResponse(UserResponse):
    entitlements: list["UserEntitlementResponse"] = []
    matched_personas: list["PersonaMatchResponse"] = []
    lifecycle_events: list["LifecycleEventResponse"] = []


class UserEntitlementResponse(BaseModel):
    id: UUID
    entitlement_name: str
    entitlement_type: str
    category: Optional[str] = None
    source: str
    is_privileged: bool = False
    is_exception: bool = False
    risk_level: str = "low"
    granted_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class PersonaMatchResponse(BaseModel):
    persona_id: UUID
    persona_name: str
    match_score: float
    matched_conditions: dict


class LifecycleEventResponse(BaseModel):
    id: UUID
    event_type: str
    previous_state: Optional[dict] = None
    new_state: Optional[dict] = None
    effective_date: datetime
    detected_at: datetime

    model_config = {"from_attributes": True}


class UserSearchRequest(BaseModel):
    query: Optional[str] = None
    department: Optional[str] = None
    job_family: Optional[str] = None
    lifecycle_state: Optional[str] = None
    limit: int = 50
    offset: int = 0

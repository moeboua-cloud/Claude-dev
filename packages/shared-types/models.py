"""Shared type definitions used across packages.

These Pydantic models serve as the contract between the API, policy engine,
agent core, and connector SDK packages.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(str, Enum):
    ADD = "add"
    REMOVE = "remove"
    REVIEW = "review"
    FLAG = "flag"


class LifecycleState(str, Enum):
    PRE_HIRE = "pre_hire"
    ACTIVE = "active"
    MOVER = "mover"
    LEAVER = "leaver"
    TERMINATED = "terminated"


class NormalizedUser(BaseModel):
    id: UUID
    employee_id: str
    email: str
    display_name: str
    department: Optional[str] = None
    job_family: Optional[str] = None
    sub_job_family: Optional[str] = None
    worker_type: str = "employee"
    lifecycle_state: LifecycleState = LifecycleState.ACTIVE
    region: Optional[str] = None


class NormalizedEntitlement(BaseModel):
    id: UUID
    name: str
    entitlement_type: str
    source_system: str
    source_identifier: str
    is_privileged: bool = False
    risk_level: RiskLevel = RiskLevel.LOW


class PolicyEvaluationResult(BaseModel):
    rule_name: str
    result: str  # allow, deny, require_approval
    reason: str
    risk_level: RiskLevel
    approvers: list[str] = []


class RecommendationPayload(BaseModel):
    user_id: UUID
    recommendation_type: ActionType
    category: str
    title: str
    description: str
    evidence: dict[str, Any]
    risk_level: RiskLevel
    confidence_score: float
    requires_approval: bool
    suggested_action: Optional[dict[str, Any]] = None


class AuditEntry(BaseModel):
    correlation_id: str
    event_type: str
    actor: str
    summary: str
    timestamp: datetime
    details: Optional[dict[str, Any]] = None
    risk_level: Optional[RiskLevel] = None

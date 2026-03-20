"""Schemas for approval workflow."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class ApprovalRequestResponse(BaseModel):
    id: UUID
    correlation_id: str
    recommendation_id: UUID
    requested_by: str
    target_user_id: UUID
    action_type: str
    action_details: dict
    risk_level: str
    required_approvers: list[str]
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ApprovalDecisionRequest(BaseModel):
    decision: str  # approved, rejected
    reason: Optional[str] = None


class ApprovalDecisionResponse(BaseModel):
    id: UUID
    approval_request_id: UUID
    approver_id: str
    approver_role: str
    decision: str
    reason: Optional[str] = None
    decided_at: datetime

    model_config = {"from_attributes": True}

"""Schemas for access comparison / variance analysis."""

from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class EntitlementVariance(BaseModel):
    entitlement_name: str
    entitlement_type: str
    status: str  # missing, excess, matched, exception
    risk_level: str = "low"
    is_privileged: bool = False
    expected_by_persona: Optional[str] = None
    evidence: dict = {}


class AccessComparisonResponse(BaseModel):
    user_id: UUID
    user_display_name: str
    matched_personas: list[str]
    total_expected: int
    total_actual: int
    missing_entitlements: list[EntitlementVariance]
    excess_entitlements: list[EntitlementVariance]
    matched_entitlements: list[EntitlementVariance]
    exception_entitlements: list[EntitlementVariance]
    overall_compliance_score: float
    risk_summary: dict

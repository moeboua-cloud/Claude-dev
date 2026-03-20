"""Access comparison / variance engine - compares actual vs expected entitlements."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import User
from app.models.entitlement import UserEntitlement
from app.schemas.comparison import AccessComparisonResponse, EntitlementVariance
from app.services.identity_service import IdentityService
from app.services.persona_service import PersonaService


class ComparisonService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.identity_svc = IdentityService(db)
        self.persona_svc = PersonaService(db)

    async def compare_user_access(self, user_id: uuid.UUID) -> AccessComparisonResponse | None:
        user = await self.identity_svc.get_user_by_id(user_id)
        if not user:
            return None

        # Get expected entitlements from persona matching
        expected = await self.persona_svc.get_expected_entitlements(user)
        matched_personas = await self.persona_svc.match_user_to_personas(user)
        persona_names = [m["persona_name"] for m in matched_personas]

        # Build lookup of expected entitlements
        expected_lookup: dict[str, dict] = {}
        for e in expected:
            key = e["entitlement_identifier"]
            expected_lookup[key] = e

        # Build lookup of actual entitlements
        actual_lookup: dict[str, UserEntitlement] = {}
        for ue in user.entitlements:
            if ue.is_active:
                actual_lookup[ue.entitlement.source_identifier] = ue

        missing = []
        excess = []
        matched_ents = []
        exceptions = []

        # Find missing and matched
        for key, exp in expected_lookup.items():
            if key in actual_lookup:
                ue = actual_lookup[key]
                if ue.is_exception:
                    exceptions.append(EntitlementVariance(
                        entitlement_name=exp["entitlement_name"],
                        entitlement_type=exp["entitlement_type"],
                        status="exception",
                        risk_level=exp["risk_level"],
                        is_privileged=exp["is_privileged"],
                        expected_by_persona=exp["source_persona"],
                        evidence={"reason": "Exception entitlement matching baseline"},
                    ))
                else:
                    matched_ents.append(EntitlementVariance(
                        entitlement_name=exp["entitlement_name"],
                        entitlement_type=exp["entitlement_type"],
                        status="matched",
                        risk_level=exp["risk_level"],
                        is_privileged=exp["is_privileged"],
                        expected_by_persona=exp["source_persona"],
                        evidence={"source": ue.source},
                    ))
            else:
                missing.append(EntitlementVariance(
                    entitlement_name=exp["entitlement_name"],
                    entitlement_type=exp["entitlement_type"],
                    status="missing",
                    risk_level=exp["risk_level"],
                    is_privileged=exp["is_privileged"],
                    expected_by_persona=exp["source_persona"],
                    evidence={"expected_by": exp["source_persona"]},
                ))

        # Find excess (actual but not expected)
        for key, ue in actual_lookup.items():
            if key not in expected_lookup:
                ent = ue.entitlement
                if ue.is_exception:
                    exceptions.append(EntitlementVariance(
                        entitlement_name=ent.name,
                        entitlement_type=ent.entitlement_type,
                        status="exception",
                        risk_level=ent.risk_level,
                        is_privileged=ent.is_privileged,
                        evidence={"reason": ue.exception_reason or "Approved exception"},
                    ))
                else:
                    excess.append(EntitlementVariance(
                        entitlement_name=ent.name,
                        entitlement_type=ent.entitlement_type,
                        status="excess",
                        risk_level=ent.risk_level,
                        is_privileged=ent.is_privileged,
                        evidence={"source": ue.source, "granted_at": str(ue.granted_at) if ue.granted_at else None},
                    ))

        total_expected = len(expected_lookup)
        total_actual = len(actual_lookup)
        compliance = len(matched_ents) / max(total_expected, 1)

        risk_summary = {
            "critical_excess": sum(1 for e in excess if e.risk_level == "critical"),
            "high_excess": sum(1 for e in excess if e.risk_level == "high"),
            "missing_required": sum(1 for m in missing if expected_lookup.get(m.entitlement_name, {}).get("is_required", False)),
            "privileged_excess": sum(1 for e in excess if e.is_privileged),
        }

        return AccessComparisonResponse(
            user_id=user.id,
            user_display_name=user.display_name,
            matched_personas=persona_names,
            total_expected=total_expected,
            total_actual=total_actual,
            missing_entitlements=missing,
            excess_entitlements=excess,
            matched_entitlements=matched_ents,
            exception_entitlements=exceptions,
            overall_compliance_score=round(compliance, 2),
            risk_summary=risk_summary,
        )

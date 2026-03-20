"""Recommendation engine - generates remediation recommendations from access variances."""

import uuid
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation
from app.models.identity import User
from app.schemas.comparison import AccessComparisonResponse, EntitlementVariance
from app.services.comparison_service import ComparisonService
from app.engine.policy_engine import PolicyEngine
from app.core.correlation import get_correlation_id


class RecommendationEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.comparison_svc = ComparisonService(db)
        self.policy_engine = PolicyEngine(db)

    async def generate_recommendations(self, user_id: uuid.UUID) -> list[Recommendation]:
        """Generate recommendations for a user based on access variance analysis."""
        comparison = await self.comparison_svc.compare_user_access(user_id)
        if not comparison:
            return []

        recommendations = []
        correlation_id = get_correlation_id()

        # Missing baseline entitlements
        for missing in comparison.missing_entitlements:
            rec = await self._create_missing_recommendation(user_id, missing, correlation_id)
            recommendations.append(rec)

        # Excess entitlements
        for excess in comparison.excess_entitlements:
            rec = await self._create_excess_recommendation(user_id, excess, correlation_id)
            recommendations.append(rec)

        # Exception entitlements needing review
        for exc in comparison.exception_entitlements:
            rec = await self._create_exception_review_recommendation(user_id, exc, correlation_id)
            recommendations.append(rec)

        for rec in recommendations:
            self.db.add(rec)
        await self.db.flush()

        return recommendations

    async def _create_missing_recommendation(
        self, user_id: uuid.UUID, variance: EntitlementVariance, correlation_id: str
    ) -> Recommendation:
        risk = variance.risk_level
        requires_approval = risk in ("medium", "high", "critical") or variance.is_privileged

        return Recommendation(
            correlation_id=correlation_id,
            user_id=user_id,
            recommendation_type="add",
            category="missing_baseline",
            title=f"Missing baseline entitlement: {variance.entitlement_name}",
            description=(
                f"User is missing expected baseline entitlement '{variance.entitlement_name}' "
                f"based on persona '{variance.expected_by_persona}'. "
                f"This is a {variance.entitlement_type} entitlement with {risk} risk level."
            ),
            evidence={
                "variance_type": "missing",
                "entitlement_name": variance.entitlement_name,
                "entitlement_type": variance.entitlement_type,
                "expected_by_persona": variance.expected_by_persona,
                "risk_level": risk,
            },
            risk_level=risk,
            confidence_score=0.95 if variance.expected_by_persona else 0.7,
            requires_approval=requires_approval,
            suggested_action={
                "action": "add",
                "entitlement_name": variance.entitlement_name,
                "entitlement_type": variance.entitlement_type,
            },
        )

    async def _create_excess_recommendation(
        self, user_id: uuid.UUID, variance: EntitlementVariance, correlation_id: str
    ) -> Recommendation:
        risk = variance.risk_level
        confidence = 0.9 if variance.is_privileged else 0.75

        return Recommendation(
            correlation_id=correlation_id,
            user_id=user_id,
            recommendation_type="remove",
            category="excess_access",
            title=f"Excess entitlement: {variance.entitlement_name}",
            description=(
                f"User has entitlement '{variance.entitlement_name}' which is not part of their "
                f"expected baseline access. This is a {variance.entitlement_type} entitlement "
                f"with {risk} risk level."
                + (" This is a PRIVILEGED entitlement." if variance.is_privileged else "")
            ),
            evidence={
                "variance_type": "excess",
                "entitlement_name": variance.entitlement_name,
                "entitlement_type": variance.entitlement_type,
                "is_privileged": variance.is_privileged,
                "risk_level": risk,
                "additional": variance.evidence,
            },
            risk_level=risk,
            confidence_score=confidence,
            requires_approval=True,
            suggested_action={
                "action": "remove",
                "entitlement_name": variance.entitlement_name,
                "entitlement_type": variance.entitlement_type,
            },
        )

    async def _create_exception_review_recommendation(
        self, user_id: uuid.UUID, variance: EntitlementVariance, correlation_id: str
    ) -> Recommendation:
        return Recommendation(
            correlation_id=correlation_id,
            user_id=user_id,
            recommendation_type="review",
            category="exception_review",
            title=f"Exception review: {variance.entitlement_name}",
            description=(
                f"User has exception entitlement '{variance.entitlement_name}' that requires periodic review. "
                f"Risk level: {variance.risk_level}."
            ),
            evidence={
                "variance_type": "exception",
                "entitlement_name": variance.entitlement_name,
                "risk_level": variance.risk_level,
                "additional": variance.evidence,
            },
            risk_level=variance.risk_level,
            confidence_score=1.0,
            requires_approval=False,
            suggested_action={"action": "review"},
        )

    async def get_recommendations_for_user(self, user_id: uuid.UUID) -> list[Recommendation]:
        stmt = (
            select(Recommendation)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_pending_recommendations(self, limit: int = 50, offset: int = 0) -> tuple[list[Recommendation], int]:
        stmt = (
            select(Recommendation)
            .where(Recommendation.status == "pending")
            .order_by(Recommendation.risk_level.desc(), Recommendation.created_at.desc())
        )
        count_result = await self.db.execute(
            select(Recommendation.id).where(Recommendation.status == "pending")
        )
        total = len(count_result.all())

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

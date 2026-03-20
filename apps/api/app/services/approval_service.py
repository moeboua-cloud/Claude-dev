"""Approval workflow service."""

import uuid
from datetime import datetime, timedelta, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import ApprovalRequest, ApprovalDecision
from app.models.recommendation import Recommendation
from app.models.action import ActionRecord
from app.core.config import get_settings
from app.core.correlation import get_correlation_id


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_approval_request(
        self,
        recommendation_id: uuid.UUID,
        requested_by: str,
    ) -> ApprovalRequest:
        # Fetch the recommendation
        rec = await self.db.get(Recommendation, recommendation_id)
        if not rec:
            raise ValueError(f"Recommendation {recommendation_id} not found")

        correlation_id = get_correlation_id()
        approvers = ["manager"]
        if rec.risk_level in ("high", "critical"):
            approvers.extend(["app_owner", "iam_admin"])

        request = ApprovalRequest(
            correlation_id=correlation_id,
            recommendation_id=recommendation_id,
            requested_by=requested_by,
            target_user_id=rec.user_id,
            action_type=rec.recommendation_type,
            action_details=rec.suggested_action or {},
            risk_level=rec.risk_level,
            required_approvers=approvers,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        self.db.add(request)

        # Update recommendation status
        rec.status = "pending_approval"
        await self.db.flush()

        return request

    async def decide_approval(
        self,
        approval_request_id: uuid.UUID,
        approver_id: str,
        approver_role: str,
        decision: str,
        reason: str | None = None,
    ) -> ApprovalDecision:
        request = await self.db.get(ApprovalRequest, approval_request_id)
        if not request:
            raise ValueError(f"Approval request {approval_request_id} not found")
        if request.status != "pending":
            raise ValueError(f"Approval request is already {request.status}")

        decision_record = ApprovalDecision(
            approval_request_id=approval_request_id,
            approver_id=approver_id,
            approver_role=approver_role,
            decision=decision,
            reason=reason,
        )
        self.db.add(decision_record)

        # Update request status
        if decision == "approved":
            request.status = "approved"
            # Update the recommendation too
            rec = await self.db.get(Recommendation, request.recommendation_id)
            if rec:
                rec.status = "approved"
        elif decision == "rejected":
            request.status = "rejected"
            rec = await self.db.get(Recommendation, request.recommendation_id)
            if rec:
                rec.status = "rejected"

        await self.db.flush()
        return decision_record

    async def get_pending_approvals(self, limit: int = 50, offset: int = 0) -> tuple[list[ApprovalRequest], int]:
        stmt = (
            select(ApprovalRequest)
            .where(ApprovalRequest.status == "pending")
            .order_by(ApprovalRequest.created_at.desc())
        )
        count_result = await self.db.execute(
            select(ApprovalRequest.id).where(ApprovalRequest.status == "pending")
        )
        total = len(count_result.all())
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    async def get_approval_by_id(self, approval_id: uuid.UUID) -> ApprovalRequest | None:
        return await self.db.get(ApprovalRequest, approval_id)

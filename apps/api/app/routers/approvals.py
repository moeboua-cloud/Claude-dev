"""Approval workflow endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.approval_service import ApprovalService
from app.services.action_service import ActionService
from app.services.audit_service import AuditService
from app.schemas.approval import ApprovalRequestResponse, ApprovalDecisionRequest, ApprovalDecisionResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalRequestResponse])
async def list_pending_approvals(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = ApprovalService(db)
    approvals, total = await svc.get_pending_approvals(limit, offset)
    return [ApprovalRequestResponse.model_validate(a) for a in approvals]


@router.post("/request/{recommendation_id}", response_model=ApprovalRequestResponse)
async def create_approval_request(
    recommendation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = ApprovalService(db)
    audit = AuditService(db)
    try:
        request = await svc.create_approval_request(recommendation_id, current_user["sub"])
        await audit.log(
            event_type="approval_requested",
            actor=current_user["sub"],
            actor_role=current_user.get("role"),
            summary=f"Approval requested for recommendation {recommendation_id}",
            target_type="recommendation",
            target_id=str(recommendation_id),
        )
        return ApprovalRequestResponse.model_validate(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{approval_id}/decide", response_model=ApprovalDecisionResponse)
async def decide_approval(
    approval_id: uuid.UUID,
    body: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = ApprovalService(db)
    audit = AuditService(db)
    try:
        decision = await svc.decide_approval(
            approval_id,
            approver_id=current_user["sub"],
            approver_role=current_user.get("role", "analyst"),
            decision=body.decision,
            reason=body.reason,
        )
        await audit.log(
            event_type="approval_decision",
            actor=current_user["sub"],
            actor_role=current_user.get("role"),
            summary=f"Approval {body.decision} for request {approval_id}",
            target_type="approval_request",
            target_id=str(approval_id),
            details={"decision": body.decision, "reason": body.reason},
        )
        return ApprovalDecisionResponse.model_validate(decision)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{approval_id}/execute")
async def execute_approved_action(
    approval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    action_svc = ActionService(db)
    audit = AuditService(db)
    try:
        record = await action_svc.execute_action(approval_id, current_user["sub"])
        await audit.log(
            event_type="action_executed",
            actor=current_user["sub"],
            actor_role=current_user.get("role"),
            summary=f"Action executed for approval {approval_id} (mode: {record.execution_mode})",
            target_type="approval_request",
            target_id=str(approval_id),
            details={"execution_mode": record.execution_mode, "result": record.result},
            outcome=record.result,
        )
        return {
            "id": str(record.id),
            "action_type": record.action_type,
            "execution_mode": record.execution_mode,
            "result": record.result,
            "result_details": record.result_details,
            "rollback_info": record.rollback_info,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

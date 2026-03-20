"""Action execution service - controlled execution of approved remediations."""

import uuid
from datetime import datetime, UTC
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action import ActionRecord
from app.models.approval import ApprovalRequest
from app.core.config import get_settings
from app.core.correlation import get_correlation_id


class ActionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def execute_action(
        self,
        approval_request_id: uuid.UUID,
        executed_by: str,
    ) -> ActionRecord:
        """Execute an approved action. Respects the global action_mode setting."""
        request = await self.db.get(ApprovalRequest, approval_request_id)
        if not request:
            raise ValueError(f"Approval request {approval_request_id} not found")
        if request.status != "approved":
            raise ValueError(f"Cannot execute: approval status is '{request.status}'")

        mode = self.settings.action_mode
        correlation_id = get_correlation_id()

        if mode == "read_only":
            raise ValueError("Action execution is disabled (read_only mode)")

        record = ActionRecord(
            correlation_id=correlation_id,
            approval_request_id=approval_request_id,
            action_type=request.action_type,
            target_user_id=request.target_user_id,
            execution_mode="simulation" if mode in ("simulation", "approval_required") else "execution",
            input_payload=request.action_details,
            executed_by=executed_by,
            result="simulated" if mode == "simulation" else "success",
            result_details=self._simulate_action(request.action_type, request.action_details),
            rollback_info={
                "action_type": "reverse_" + request.action_type,
                "details": request.action_details,
            },
        )
        self.db.add(record)
        await self.db.flush()

        return record

    def _simulate_action(self, action_type: str, details: dict) -> dict:
        """Simulate an action and return what would happen."""
        ent_name = details.get("entitlement_name", "unknown")
        if action_type == "add":
            return {
                "simulation": True,
                "would_add": ent_name,
                "target_system": self._infer_target_system(ent_name),
                "estimated_propagation": "5-15 minutes",
            }
        elif action_type == "remove":
            return {
                "simulation": True,
                "would_remove": ent_name,
                "target_system": self._infer_target_system(ent_name),
                "estimated_propagation": "5-15 minutes",
                "reversible": True,
            }
        return {"simulation": True, "action": action_type, "details": details}

    def _infer_target_system(self, entitlement_name: str) -> str:
        if entitlement_name.startswith("APP-"):
            return "active_directory"
        if entitlement_name.startswith("GRP-"):
            return "active_directory"
        if entitlement_name.startswith("PAM-"):
            return "delinea_pam"
        if entitlement_name.startswith("Entra-"):
            return "entra_id"
        return "unknown"

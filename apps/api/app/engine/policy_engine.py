"""Deterministic policy engine - evaluates actions against governance rules.

The policy engine is the gatekeeper. It does NOT use AI/LLM for decisions.
All policy evaluations are deterministic, auditable, and based on configured rules.
"""

import uuid
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.policy import PolicyRule, PolicyEvaluation
from app.core.correlation import get_correlation_id


# Default built-in policy rules (loaded if DB has no rules)
DEFAULT_POLICIES = [
    {
        "name": "high_risk_action_requires_approval",
        "description": "Any action on high or critical risk entitlements requires approval",
        "rule_type": "action_gate",
        "conditions": {"risk_level": ["high", "critical"]},
        "actions": {"result": "require_approval", "approvers": ["manager", "iam_admin"]},
        "risk_level": "high",
        "priority": 10,
    },
    {
        "name": "privileged_access_requires_approval",
        "description": "Granting any privileged access requires multi-level approval",
        "rule_type": "action_gate",
        "conditions": {"is_privileged": True},
        "actions": {"result": "require_approval", "approvers": ["manager", "app_owner", "iam_admin"]},
        "risk_level": "high",
        "priority": 20,
    },
    {
        "name": "contractor_privileged_access_denied",
        "description": "Contractors cannot hold privileged group memberships",
        "rule_type": "sod",
        "conditions": {"worker_type": "contractor", "is_privileged": True},
        "actions": {"result": "deny", "reason": "Contractors cannot hold privileged access"},
        "risk_level": "critical",
        "priority": 5,
    },
    {
        "name": "low_risk_removal_auto_approve",
        "description": "Low-risk entitlement removals can be auto-approved in simulation mode",
        "rule_type": "action_gate",
        "conditions": {"action": "remove", "risk_level": ["low"]},
        "actions": {"result": "allow"},
        "risk_level": "low",
        "priority": 50,
    },
    {
        "name": "mover_stale_access_review",
        "description": "Users in mover state must have stale access reviewed",
        "rule_type": "risk_threshold",
        "conditions": {"lifecycle_state": "mover", "has_stale_access": True},
        "actions": {"result": "require_approval", "approvers": ["manager"]},
        "risk_level": "medium",
        "priority": 30,
    },
    {
        "name": "sod_finance_admin_and_it_admin",
        "description": "No user should have both SAP Finance Admin and Domain Admin",
        "rule_type": "sod",
        "conditions": {
            "entitlements_all": ["APP-SAP-FinanceAdmin", "GRP-DomainAdmins"],
        },
        "actions": {"result": "deny", "reason": "Separation of Duties violation: Finance Admin + Domain Admin"},
        "risk_level": "critical",
        "priority": 1,
    },
]


class PolicyEngine:
    """Deterministic policy evaluation engine."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_action(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Evaluate an action context against all active policy rules.

        Args:
            context: Dictionary with action details, e.g.:
                {
                    "action": "add" | "remove",
                    "target_user_id": "...",
                    "entitlement_name": "...",
                    "risk_level": "low" | "medium" | "high" | "critical",
                    "is_privileged": bool,
                    "worker_type": "employee" | "contractor",
                    "lifecycle_state": "active" | "mover" | ...,
                }

        Returns:
            List of policy evaluation results, each with:
                {"rule_name", "result", "reason", "risk_level"}
        """
        rules = await self._get_active_rules()
        evaluations = []
        correlation_id = get_correlation_id()

        for rule in rules:
            match = self._evaluate_rule(rule, context)
            if match is not None:
                eval_record = PolicyEvaluation(
                    correlation_id=correlation_id,
                    policy_rule_id=rule.get("id"),
                    policy_rule_name=rule["name"],
                    input_context=context,
                    result=match["result"],
                    reason=match["reason"],
                    risk_level=match["risk_level"],
                )
                self.db.add(eval_record)
                evaluations.append(match)

        await self.db.flush()
        return evaluations

    def _evaluate_rule(self, rule: dict, context: dict) -> dict | None:
        """Check if a single rule matches the given context."""
        conditions = rule.get("conditions", {})
        actions = rule.get("actions", {})

        for key, expected in conditions.items():
            actual = context.get(key)
            if actual is None:
                return None

            if isinstance(expected, list):
                if actual not in expected:
                    return None
            elif isinstance(expected, bool):
                if bool(actual) != expected:
                    return None
            else:
                if str(actual).lower() != str(expected).lower():
                    return None

        return {
            "rule_name": rule["name"],
            "result": actions.get("result", "allow"),
            "reason": actions.get("reason", rule.get("description", "")),
            "risk_level": rule.get("risk_level", "medium"),
            "approvers": actions.get("approvers", []),
        }

    async def _get_active_rules(self) -> list[dict]:
        """Fetch active rules from DB, falling back to defaults."""
        stmt = select(PolicyRule).where(PolicyRule.is_active == True).order_by(PolicyRule.priority)
        result = await self.db.execute(stmt)
        db_rules = result.scalars().all()

        if db_rules:
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "rule_type": r.rule_type,
                    "conditions": r.conditions,
                    "actions": r.actions,
                    "risk_level": r.risk_level,
                    "priority": r.priority,
                }
                for r in db_rules
            ]

        return DEFAULT_POLICIES

    async def classify_risk(self, entitlement_name: str, is_privileged: bool, action: str) -> str:
        """Classify the risk level of an entitlement action."""
        if is_privileged:
            return "high" if action == "remove" else "critical"
        if any(prefix in entitlement_name for prefix in ["PAM-", "GRP-Domain", "Admin"]):
            return "high"
        if any(prefix in entitlement_name for prefix in ["APP-"]):
            return "medium"
        return "low"

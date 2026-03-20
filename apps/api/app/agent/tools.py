"""Agent tools - functions the AI agent can call to query IAM data and systems."""

import uuid
from typing import Any

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.identity import User
from app.models.entitlement import UserEntitlement
from app.services.identity_service import IdentityService
from app.services.persona_service import PersonaService
from app.services.comparison_service import ComparisonService
from app.engine.recommendation_engine import RecommendationEngine
from app.engine.policy_engine import PolicyEngine


TOOL_DEFINITIONS = [
    {
        "name": "lookup_user",
        "description": "Look up a user by name, email, or employee ID",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "User name, email, or employee ID"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_user_access",
        "description": "Get the full access graph for a user including all entitlements",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User UUID"},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "compare_access",
        "description": "Compare a user's actual access against their expected persona baseline",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User UUID"},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "explain_access",
        "description": "Explain why a user does or does not have a specific entitlement",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User UUID"},
                "entitlement_name": {"type": "string", "description": "Name of the entitlement to check"},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "generate_recommendations",
        "description": "Generate remediation recommendations for a user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User UUID"},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "evaluate_policy",
        "description": "Evaluate a proposed action against policy rules",
        "parameters": {
            "type": "object",
            "properties": {
                "context": {"type": "object", "description": "Action context for policy evaluation"},
            },
            "required": ["context"],
        },
    },
]


class AgentToolExecutor:
    """Executes agent tools against the IAM data layer."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.identity_svc = IdentityService(db)
        self.persona_svc = PersonaService(db)
        self.comparison_svc = ComparisonService(db)
        self.recommendation_engine = RecommendationEngine(db)
        self.policy_engine = PolicyEngine(db)

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        handler = getattr(self, f"_tool_{tool_name}", None)
        if handler is None:
            return {"error": f"Unknown tool: {tool_name}"}
        return await handler(arguments)

    async def _tool_lookup_user(self, args: dict) -> dict:
        query = args.get("query", "")
        users, total = await self.identity_svc.search_users(query=query, limit=5)
        return {
            "users": [
                {
                    "id": str(u.id),
                    "employee_id": u.employee_id,
                    "display_name": u.display_name,
                    "email": u.email,
                    "department": u.department,
                    "job_title": u.job_title,
                    "lifecycle_state": u.lifecycle_state.value if u.lifecycle_state else None,
                }
                for u in users
            ],
            "total": total,
        }

    async def _tool_get_user_access(self, args: dict) -> dict:
        user_id = uuid.UUID(args["user_id"])
        return await self.identity_svc.get_user_access_graph(user_id)

    async def _tool_compare_access(self, args: dict) -> dict:
        # Handle both user_id and query-based lookups
        user_id = args.get("user_id")
        if not user_id:
            query = args.get("query", "")
            users, _ = await self.identity_svc.search_users(query=query, limit=1)
            if not users:
                return {"error": "User not found"}
            user_id = str(users[0].id)

        comparison = await self.comparison_svc.compare_user_access(uuid.UUID(user_id))
        if not comparison:
            return {"error": "Could not generate comparison"}
        return comparison.model_dump(mode="json")

    async def _tool_explain_access(self, args: dict) -> dict:
        user_id = args.get("user_id")
        entitlement_name = args.get("entitlement_name")
        query = args.get("query", "")

        # Resolve user from query if needed
        if not user_id:
            users, _ = await self.identity_svc.search_users(query=query, limit=1)
            if not users:
                return {"error": "User not found"}
            user_id = str(users[0].id)

        user = await self.identity_svc.get_user_by_id(uuid.UUID(user_id))
        if not user:
            return {"error": "User not found"}

        # Check actual entitlements
        has_entitlement = False
        entitlement_details = None
        for ue in user.entitlements:
            if entitlement_name and entitlement_name.lower() in ue.entitlement.name.lower():
                has_entitlement = True
                entitlement_details = {
                    "name": ue.entitlement.name,
                    "source": ue.source,
                    "granted_at": str(ue.granted_at) if ue.granted_at else None,
                    "is_exception": ue.is_exception,
                }
                break

        # Check expected entitlements
        expected = await self.persona_svc.get_expected_entitlements(user)
        is_expected = False
        expected_persona = None
        if entitlement_name:
            for exp in expected:
                if entitlement_name.lower() in exp["entitlement_name"].lower():
                    is_expected = True
                    expected_persona = exp["source_persona"]
                    break

        personas = await self.persona_svc.match_user_to_personas(user)

        return {
            "user": {"display_name": user.display_name, "department": user.department, "job_family": user.job_family},
            "entitlement_query": entitlement_name,
            "has_entitlement": has_entitlement,
            "entitlement_details": entitlement_details,
            "is_expected_by_persona": is_expected,
            "expected_persona": expected_persona,
            "matched_personas": [p["persona_name"] for p in personas],
            "explanation": self._build_explanation(
                user.display_name, entitlement_name, has_entitlement, is_expected, expected_persona
            ),
        }

    def _build_explanation(
        self, user_name: str, ent_name: str | None, has: bool, expected: bool, persona: str | None
    ) -> str:
        if not ent_name:
            return f"Please specify an entitlement to explain access for {user_name}."

        if has and expected:
            return (
                f"{user_name} has '{ent_name}' access, which is expected based on their "
                f"persona mapping to '{persona}'. This entitlement is part of their baseline access."
            )
        elif has and not expected:
            return (
                f"{user_name} has '{ent_name}' access, but this is NOT part of their expected baseline. "
                f"This may be excess access that should be reviewed for removal."
            )
        elif not has and expected:
            return (
                f"{user_name} does NOT have '{ent_name}' access, but it IS expected based on their "
                f"persona mapping to '{persona}'. This is missing baseline access that should be provisioned."
            )
        else:
            return (
                f"{user_name} does not have '{ent_name}' access, and it is not expected based on their "
                f"current persona mapping. No action is needed."
            )

    async def _tool_generate_recommendations(self, args: dict) -> dict:
        user_id = args.get("user_id")
        if not user_id:
            query = args.get("query", "")
            users, _ = await self.identity_svc.search_users(query=query, limit=1)
            if not users:
                return {"error": "User not found"}
            user_id = str(users[0].id)

        recs = await self.recommendation_engine.generate_recommendations(uuid.UUID(user_id))
        return {
            "recommendations": [
                {
                    "id": str(r.id),
                    "type": r.recommendation_type,
                    "category": r.category,
                    "title": r.title,
                    "risk_level": r.risk_level,
                    "confidence": r.confidence_score,
                    "requires_approval": r.requires_approval,
                }
                for r in recs
            ],
            "total": len(recs),
        }

    async def _tool_evaluate_policy(self, args: dict) -> dict:
        context = args.get("context", {})
        results = await self.policy_engine.evaluate_action(context)
        return {"evaluations": results}

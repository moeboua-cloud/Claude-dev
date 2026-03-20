"""IAM Agent - the reasoning layer that interprets natural language and orchestrates tools.

Safety model:
- Agent NEVER directly executes high-risk actions
- Agent gathers evidence and makes recommendations
- All actions flow through policy engine -> approval -> execution pipeline
- Agent responses distinguish facts, inferences, and recommendations
"""

from datetime import datetime, UTC
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm_provider import get_llm_provider, BaseLLMProvider
from app.agent.tools import AgentToolExecutor, TOOL_DEFINITIONS
from app.services.audit_service import AuditService
from app.schemas.chat import ChatResponse, EvidenceItem
from app.core.correlation import get_correlation_id


SYSTEM_PROMPT = """You are an IAM (Identity and Access Management) analyst assistant.
You help analysts troubleshoot access issues, compare user access against baselines,
detect anomalies, and recommend remediations.

Rules:
1. Always base your answers on evidence from the IAM data systems.
2. Clearly distinguish between observed facts, policy evaluations, and inferred conclusions.
3. Never recommend bypassing security policies.
4. For high-risk changes, always recommend the approval workflow.
5. Provide concise, actionable answers suitable for audit records.
6. If uncertain, state your confidence level and suggest verification steps.
"""


class IAMAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = get_llm_provider()
        self.tool_executor = AgentToolExecutor(db)
        self.audit_svc = AuditService(db)

    async def process_query(
        self, message: str, actor: str, context: dict | None = None
    ) -> ChatResponse:
        correlation_id = get_correlation_id()

        # Log the query
        await self.audit_svc.log(
            event_type="query",
            actor=actor,
            summary=f"Analyst query: {message[:200]}",
            details={"message": message, "context": context},
        )

        # Classify intent and determine what tools to call
        intent = self._classify_intent(message)
        evidence_items: list[EvidenceItem] = []
        tool_results: list[dict] = []

        # Execute tools based on intent
        user_id = context.get("user_id") if context else None

        if intent == "explain_access":
            result = await self._handle_explain(message, user_id)
            tool_results.append(result)

        elif intent == "compare_access":
            result = await self._handle_compare(message, user_id)
            tool_results.append(result)

        elif intent == "recommend":
            result = await self._handle_recommend(message, user_id)
            tool_results.append(result)

        elif intent == "lookup_user":
            result = await self.tool_executor.execute_tool("lookup_user", {"query": message})
            tool_results.append(result)

        else:
            # General query - try user lookup first
            result = await self.tool_executor.execute_tool("lookup_user", {"query": message})
            tool_results.append(result)

        # Build evidence from tool results
        for result in tool_results:
            if "error" not in result:
                evidence_items.append(EvidenceItem(
                    source="iam_data",
                    description=f"Tool result for intent: {intent}",
                    data=result,
                    confidence=0.95,
                ))

        # Build response
        answer = self._build_answer(intent, tool_results, message)
        policy_evals = []
        recommendations = []
        suggested_actions = []
        risk_level = None

        # Extract recommendations and risk from tool results
        for result in tool_results:
            if "recommendations" in result:
                recommendations = result["recommendations"]
                if recommendations:
                    risk_levels = [r.get("risk_level", "low") for r in recommendations]
                    risk_level = max(risk_levels, key=lambda x: ["low", "medium", "high", "critical"].index(x))
                    suggested_actions = [
                        {"recommendation_id": r["id"], "type": r["type"], "title": r["title"]}
                        for r in recommendations
                        if r.get("requires_approval")
                    ]

            if "overall_compliance_score" in result:
                risk_summary = result.get("risk_summary", {})
                if risk_summary.get("critical_excess", 0) > 0:
                    risk_level = "critical"
                elif risk_summary.get("high_excess", 0) > 0:
                    risk_level = "high"
                elif risk_summary.get("missing_required", 0) > 0:
                    risk_level = "medium"

        # Log the response
        await self.audit_svc.log(
            event_type="agent_response",
            actor="system",
            summary=f"Agent response for intent: {intent}",
            details={"intent": intent, "answer_length": len(answer)},
            evidence_sources=[e.source for e in evidence_items],
            risk_level=risk_level,
        )

        return ChatResponse(
            correlation_id=correlation_id,
            answer=answer,
            intent=intent,
            evidence=evidence_items,
            policy_evaluations=policy_evals,
            recommendations=recommendations,
            risk_level=risk_level,
            requires_action=len(suggested_actions) > 0,
            suggested_actions=suggested_actions,
            timestamp=datetime.now(UTC),
        )

    def _classify_intent(self, message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ["why does", "why doesn't", "why can't", "explain", "missing access"]):
            return "explain_access"
        if any(w in msg for w in ["compare", "baseline", "expected", "persona", "should have"]):
            return "compare_access"
        if any(w in msg for w in ["recommend", "cleanup", "excess", "remediat", "remove", "drift"]):
            return "recommend"
        if any(w in msg for w in ["who is", "find", "search", "look up", "show me"]):
            return "lookup_user"
        if any(w in msg for w in ["audit", "timeline", "history", "evidence"]):
            return "audit_query"
        if any(w in msg for w in ["what changed", "mover", "moved", "transfer"]):
            return "mover_analysis"
        return "general"

    async def _handle_explain(self, message: str, user_id: str | None) -> dict:
        # Extract user and entitlement from message
        args: dict[str, Any] = {"query": message}
        if user_id:
            args["user_id"] = user_id

        # Try to extract app/entitlement name from message
        keywords = ["epic", "sap", "jira", "github", "servicenow", "workday", "slack", "teams", "salesforce"]
        for kw in keywords:
            if kw in message.lower():
                args["entitlement_name"] = kw
                break

        return await self.tool_executor.execute_tool("explain_access", args)

    async def _handle_compare(self, message: str, user_id: str | None) -> dict:
        args: dict[str, Any] = {"query": message}
        if user_id:
            args["user_id"] = user_id
        return await self.tool_executor.execute_tool("compare_access", args)

    async def _handle_recommend(self, message: str, user_id: str | None) -> dict:
        args: dict[str, Any] = {"query": message}
        if user_id:
            args["user_id"] = user_id
        return await self.tool_executor.execute_tool("generate_recommendations", args)

    def _build_answer(self, intent: str, results: list[dict], original_message: str) -> str:
        """Build a human-readable answer from tool results."""
        if not results:
            return "I was unable to find relevant information. Please refine your query."

        for result in results:
            if "error" in result:
                return f"I encountered an issue: {result['error']}. Please try a more specific query."

        if intent == "explain_access":
            for r in results:
                if "explanation" in r:
                    return r["explanation"]

        if intent == "compare_access":
            for r in results:
                if "overall_compliance_score" in r:
                    score = r["overall_compliance_score"]
                    missing = len(r.get("missing_entitlements", []))
                    excess = len(r.get("excess_entitlements", []))
                    name = r.get("user_display_name", "This user")
                    personas = ", ".join(r.get("matched_personas", []))

                    parts = [
                        f"**Access Comparison for {name}**",
                        f"Matched personas: {personas}" if personas else "No persona matches found.",
                        f"Compliance score: {score:.0%}",
                        f"Missing baseline entitlements: {missing}",
                        f"Excess entitlements: {excess}",
                        f"Exception entitlements: {len(r.get('exception_entitlements', []))}",
                    ]

                    risk = r.get("risk_summary", {})
                    if risk.get("critical_excess") or risk.get("high_excess") or risk.get("privileged_excess"):
                        parts.append("\n**Risk Alerts:**")
                        if risk.get("critical_excess"):
                            parts.append(f"- {risk['critical_excess']} critical-risk excess entitlement(s)")
                        if risk.get("privileged_excess"):
                            parts.append(f"- {risk['privileged_excess']} privileged excess entitlement(s)")

                    return "\n".join(parts)

        if intent == "recommend":
            for r in results:
                if "recommendations" in r:
                    recs = r["recommendations"]
                    if not recs:
                        return "No recommendations were generated. The user's access appears aligned with their baseline."
                    parts = [f"**{len(recs)} Recommendation(s) Generated:**\n"]
                    for rec in recs:
                        risk_badge = f"[{rec['risk_level'].upper()}]"
                        approval = " (requires approval)" if rec.get("requires_approval") else ""
                        parts.append(f"- {risk_badge} {rec['title']}{approval}")
                    return "\n".join(parts)

        if intent == "lookup_user":
            for r in results:
                if "users" in r:
                    users = r["users"]
                    if not users:
                        return "No users found matching your query."
                    parts = [f"Found {r['total']} user(s):\n"]
                    for u in users:
                        parts.append(
                            f"- **{u['display_name']}** ({u['email']}) - "
                            f"{u['job_title'] or 'N/A'}, {u['department'] or 'N/A'} "
                            f"[{u['lifecycle_state']}]"
                        )
                    return "\n".join(parts)

        return "I've gathered the relevant information. Please review the evidence panel for details."

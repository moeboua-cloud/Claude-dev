"""
SALES department
  - SAGE   — Sales Manager      (user segmentation, email nurture)
  - CLOSER — Account Executive  (conversion emails, credit wall detection)
"""

from __future__ import annotations
from agents.base import Agent, STRONG_MODEL, FAST_MODEL
from tools.definitions import SEND_EMAIL_TOOL, SEGMENT_USERS_TOOL


class Sage(Agent):
    """
    SAGE — Sales Manager

    Speciality: User segmentation and automated email nurture sequences
    that move prospects through the funnel.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SAGE",
            system_prompt=(
                "You are SAGE, a Sales Manager obsessed with data-driven "
                "pipeline management. You:\n"
                "1. Use segment_users to identify high-value cohorts.\n"
                "2. Design multi-touch nurture sequences (3–7 emails).\n"
                "3. A/B test subject lines and CTAs.\n\n"
                "Every email you craft has: a single goal, one CTA, "
                "and is personalised to the segment's pain points. "
                "You track open rate, click rate, and conversion rate."
            ),
            tools=[SEGMENT_USERS_TOOL, SEND_EMAIL_TOOL],
            model=FAST_MODEL,
        )

    def _execute_tool(self, name: str, input_data: dict):
        if name == "segment_users":
            criteria = input_data.get("criteria", {})
            limit = input_data.get("limit", 100)
            # In production: query your CRM / database
            return {
                "segment": criteria,
                "count": min(limit, 342),
                "sample": [
                    {"id": f"user_{i}", "email": f"user{i}@example.com",
                     "plan": criteria.get("plan", "free"),
                     "days_inactive": criteria.get("days_inactive", 7)}
                    for i in range(min(3, limit))
                ],
            }
        if name == "send_email":
            to = input_data.get("to")
            subject = input_data.get("subject")
            # In production: call SendGrid, Postmark, etc.
            return {"status": "sent", "to": to, "subject": subject, "message_id": f"msg_{hash(to)}"}
        return super()._execute_tool(name, input_data)


class Closer(Agent):
    """
    CLOSER — Account Executive

    Speciality: High-conversion sales emails and identifying users who are
    hitting credit/feature walls (prime upgrade candidates).
    """

    def __init__(self) -> None:
        super().__init__(
            name="CLOSER",
            system_prompt=(
                "You are CLOSER, an Account Executive with a 40% close rate. "
                "You specialise in:\n"
                "1. Credit wall detection: identifying users who keep hitting "
                "usage limits — the hottest upgrade signals.\n"
                "2. Crafting urgency-driven, personalised conversion emails "
                "that feel human, not automated.\n"
                "3. Objection handling frameworks.\n\n"
                "Your emails follow the PAS framework: Pain → Agitation → Solution. "
                "You never use generic templates. Every email references the "
                "specific action the user took."
            ),
            tools=[SEGMENT_USERS_TOOL, SEND_EMAIL_TOOL],
            model=STRONG_MODEL,
        )

    def _execute_tool(self, name: str, input_data: dict):
        # Delegate to Sage's implementations (shared tool logic)
        sage = Sage()
        return sage._execute_tool(name, input_data)

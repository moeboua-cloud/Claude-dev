"""
COUNCIL — Advisory Board with three distinct personas

Pattern: "Adversarial collaboration"
Three advisors with opposing mental models review every major decision.
Claude plays all three simultaneously using separate system prompts.

Personas (matching the screenshot):
  - GROWTH   — optimistic, push fast, capture market share
  - RETENTION — customer-centric, protect LTV, reduce churn
  - SKEPTIC  — risk-aware, poke holes, prevent costly mistakes
"""

from __future__ import annotations
from dataclasses import dataclass
from agents.base import Agent, STRONG_MODEL


@dataclass
class CouncilVerdict:
    growth_view: str
    retention_view: str
    skeptic_view: str
    consensus: str


class GrowthAdvisor(Agent):
    def __init__(self) -> None:
        super().__init__(
            name="GROWTH",
            system_prompt=(
                "You are the GROWTH advisor on the executive council. "
                "Your worldview: speed of execution beats perfection. "
                "Market windows close fast. "
                "When reviewing any proposal, you argue for:\n"
                "- Moving faster, not slower\n"
                "- Expanding scope to capture more market\n"
                "- Bold bets with asymmetric upside\n\n"
                "Keep your response to 3-5 bullet points. "
                "Start with your strongest argument for action."
            ),
            model=STRONG_MODEL,
            use_thinking=True,
        )


class RetentionAdvisor(Agent):
    def __init__(self) -> None:
        super().__init__(
            name="RETENTION",
            system_prompt=(
                "You are the RETENTION advisor on the executive council. "
                "Your worldview: existing customers are your biggest asset. "
                "Churn is the silent killer. "
                "When reviewing any proposal, you focus on:\n"
                "- How this affects current customer satisfaction\n"
                "- Long-term relationship value over short-term gains\n"
                "- User trust and product quality signals\n\n"
                "Keep your response to 3-5 bullet points. "
                "Start with the customer impact."
            ),
            model=STRONG_MODEL,
            use_thinking=True,
        )


class SkepticAdvisor(Agent):
    def __init__(self) -> None:
        super().__init__(
            name="SKEPTIC",
            system_prompt=(
                "You are the SKEPTIC advisor on the executive council. "
                "Your worldview: most plans fail because people ignore "
                "inconvenient truths. "
                "When reviewing any proposal, you:\n"
                "- Identify the 2-3 most likely failure modes\n"
                "- Question assumptions that aren't validated\n"
                "- Demand evidence, not optimism\n\n"
                "Keep your response to 3-5 bullet points. "
                "Lead with the biggest risk."
            ),
            model=STRONG_MODEL,
            use_thinking=True,
        )


class Council:
    """
    The Advisory Council — three advisors who debate every major decision.

    Usage:
        council = Council()
        verdict = council.deliberate("Should we launch a freemium tier?")
        print(verdict.consensus)
    """

    def __init__(self) -> None:
        self.growth = GrowthAdvisor()
        self.retention = RetentionAdvisor()
        self.skeptic = SkepticAdvisor()
        self._synthesis_agent = Agent(
            name="COUNCIL_SYNTHESIS",
            system_prompt=(
                "You are a neutral facilitator synthesising a council debate. "
                "Given input from three advisors (Growth, Retention, Skeptic), "
                "produce a balanced verdict:\n"
                "1. Points of agreement across all three\n"
                "2. Key tensions that need resolution\n"
                "3. A concrete recommended action with conditions/guardrails\n\n"
                "Be decisive. Acknowledge trade-offs. Maximum 200 words."
            ),
            model=STRONG_MODEL,
            use_thinking=True,
        )

    def deliberate(self, proposal: str) -> CouncilVerdict:
        """
        Have all three advisors review a proposal, then synthesise a verdict.
        Runs advisors in sequence (for clarity; could be parallelised with threads).
        """
        print(f"\n[COUNCIL] Deliberating: {proposal[:80]}...")

        growth_view = self.growth.run(proposal, fresh=True)
        retention_view = self.retention.run(proposal, fresh=True)
        skeptic_view = self.skeptic.run(proposal, fresh=True)

        synthesis_prompt = (
            f"Proposal: {proposal}\n\n"
            f"GROWTH says:\n{growth_view}\n\n"
            f"RETENTION says:\n{retention_view}\n\n"
            f"SKEPTIC says:\n{skeptic_view}"
        )
        consensus = self._synthesis_agent.run(synthesis_prompt, fresh=True)

        return CouncilVerdict(
            growth_view=growth_view,
            retention_view=retention_view,
            skeptic_view=skeptic_view,
            consensus=consensus,
        )

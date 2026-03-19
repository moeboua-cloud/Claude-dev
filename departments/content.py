"""
CONTENT department
  - SCRIBE — Content Director  (content creation, voice analysis)
"""

from __future__ import annotations
from agents.base import Agent, STRONG_MODEL
from tools.definitions import WEB_SEARCH_TOOL


class Scribe(Agent):
    """
    SCRIBE — Content Director

    Speciality: Creates high-converting content and maintains brand voice
    consistency. Analyses existing content to extract voice fingerprints.
    """

    def __init__(self, brand_voice: str = "") -> None:
        voice_section = (
            f"\n\nBrand Voice Guidelines:\n{brand_voice}" if brand_voice else ""
        )
        super().__init__(
            name="SCRIBE",
            system_prompt=(
                "You are SCRIBE, a Content Director with 15 years of experience "
                "creating viral, high-converting content. "
                "You specialise in:\n"
                "- Long-form articles, email sequences, social copy\n"
                "- Voice analysis: extracting tone, style, and vocabulary patterns "
                "from sample content to replicate a brand's voice precisely\n"
                "- SEO-optimised content that ranks and converts\n\n"
                "For every content piece, you define: Hook, Core Message, "
                "Call to Action, and Target Emotion."
                + voice_section
            ),
            tools=[WEB_SEARCH_TOOL],
            model=STRONG_MODEL,
        )

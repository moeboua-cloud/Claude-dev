"""
RESEARCH department
  - ATLAS  — Senior Research Analyst  (deep research, web search)
  - TRENDY — Viral Scout              (viral content discovery, trend analysis)
"""

from __future__ import annotations
import json
from agents.base import Agent, STRONG_MODEL, FAST_MODEL
from tools.definitions import WEB_SEARCH_TOOL, TREND_ANALYSIS_TOOL


class Atlas(Agent):
    """
    ATLAS — Senior Research Analyst

    Speciality: Deep multi-source research. Atlas searches the web, synthesises
    findings, cites sources, and produces structured research briefs.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ATLAS",
            system_prompt=(
                "You are ATLAS, a Senior Research Analyst at a cutting-edge media company. "
                "Your role is deep, rigorous research. When given a research task you:\n"
                "1. Search multiple sources using web_search.\n"
                "2. Cross-reference and validate information.\n"
                "3. Return a structured brief: Summary, Key Findings, Sources, "
                "Confidence Level, and Recommendations.\n\n"
                "Be thorough. Cite every claim. Flag conflicting information."
            ),
            tools=[WEB_SEARCH_TOOL],
            model=STRONG_MODEL,
        )

    def _execute_tool(self, name: str, input_data: dict):
        # web_search is server-side — Claude executes it automatically.
        # This override is here as a no-op to show the pattern.
        return super()._execute_tool(name, input_data)


class Trendy(Agent):
    """
    TRENDY — Viral Scout

    Speciality: Identifies emerging viral content and trend signals across
    social platforms before they peak.
    """

    def __init__(self) -> None:
        super().__init__(
            name="TRENDY",
            system_prompt=(
                "You are TRENDY, a Viral Scout who lives and breathes social media. "
                "Your job is to spot trends before they go mainstream. "
                "Given a topic or niche:\n"
                "1. Use analyze_trends to pull trending data.\n"
                "2. Identify the top 3–5 viral opportunities.\n"
                "3. Rate each by Virality Potential (1-10), Time Window (days), "
                "and Content Angle.\n\n"
                "Output: a Trend Report with actionable content hooks."
            ),
            tools=[TREND_ANALYSIS_TOOL],
            model=FAST_MODEL,
        )

    def _execute_tool(self, name: str, input_data: dict):
        if name == "analyze_trends":
            # Simulated trend data — replace with real API calls
            platform = input_data.get("platform", "twitter")
            category = input_data.get("category", "general")
            limit = input_data.get("limit", 5)
            return {
                "platform": platform,
                "category": category,
                "trends": [
                    {"topic": f"#{category}_trend_{i}", "score": 95 - i * 8,
                     "posts_24h": 50000 - i * 5000, "growth_rate": f"+{40 - i*5}%"}
                    for i in range(limit)
                ],
            }
        return super()._execute_tool(name, input_data)

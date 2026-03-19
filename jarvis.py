"""
JARVIS — Chief Strategy Officer & Task Orchestrator

Pattern: "Router + Planner"

JARVIS is the top-level orchestrator. When the CEO gives a task, JARVIS:
1. Breaks it into sub-tasks.
2. Routes each sub-task to the right department agent(s).
3. Decides when a question needs the Council or ORACLE.
4. Assembles results into a final executive summary.

This implements the "Orchestrator → Specialist" multi-agent pattern.
The key design choice: JARVIS uses tool_use to call agents as tools,
so Claude itself decides the routing, not hard-coded if/else logic.
"""

from __future__ import annotations
import json
from typing import Any
import anthropic

from departments import (
    Atlas, Trendy, Clawd, Sentinel, Scribe, Pixel, Nova, Vibe, Clip, Sage, Closer
)
from council import Council
from oracle import consult_oracle

client = anthropic.Anthropic()

# ── Tool definitions for JARVIS to call agents ────────────────────────────────

def _agent_tool(agent_name: str, description: str) -> dict:
    return {
        "name": f"call_{agent_name.lower()}",
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": f"The specific task or question for {agent_name}.",
                }
            },
            "required": ["task"],
        },
    }


JARVIS_TOOLS = [
    _agent_tool("atlas",    "Deep research: market research, competitor analysis, fact-finding."),
    _agent_tool("trendy",   "Viral trend scouting: identify trending topics and content opportunities."),
    _agent_tool("clawd",    "Software development: write code, review PRs, architect solutions."),
    _agent_tool("sentinel", "QA & monitoring: run tests, identify bugs, validate quality."),
    _agent_tool("scribe",   "Content creation: write articles, emails, social copy, scripts."),
    _agent_tool("pixel",    "Design: visual concepts, brand assets, image generation."),
    _agent_tool("nova",     "Video production: video strategy, scripting, production planning."),
    _agent_tool("vibe",     "Motion design: animated intros, motion graphics, launch videos."),
    _agent_tool("clip",     "Video clipping: extract short-form clips and generate captions."),
    _agent_tool("sage",     "Sales nurture: user segmentation, email sequences, pipeline management."),
    _agent_tool("closer",   "Sales conversion: convert trial users, handle credit wall triggers."),
    {
        "name": "call_council",
        "description": (
            "Escalate to the Advisory Council for major strategic decisions "
            "that need multiple perspectives (Growth vs Retention vs Risk)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "proposal": {
                    "type": "string",
                    "description": "The strategic proposal or decision to deliberate on.",
                }
            },
            "required": ["proposal"],
        },
    },
    {
        "name": "call_oracle",
        "description": (
            "Consult ORACLE for McKinsey-level strategic analysis on the hardest, "
            "most consequential questions. Use sparingly — high cost, high value."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The strategic question requiring deep analysis.",
                },
                "context": {
                    "type": "string",
                    "description": "Relevant background context.",
                },
            },
            "required": ["question"],
        },
    },
]


class Jarvis:
    """
    JARVIS — Chief Strategy Officer

    The top-level orchestrator that receives CEO directives and coordinates
    the full team of specialist agents.
    """

    def __init__(self) -> None:
        # Instantiate all specialist agents once (reuse across tasks)
        self._agents = {
            "atlas":    Atlas(),
            "trendy":   Trendy(),
            "clawd":    Clawd(),
            "sentinel": Sentinel(),
            "scribe":   Scribe(),
            "pixel":    Pixel(),
            "nova":     Nova(),
            "vibe":     Vibe(),
            "clip":     Clip(),
            "sage":     Sage(),
            "closer":   Closer(),
        }
        self._council = Council()
        self._history: list[dict] = []

    def execute(self, directive: str) -> str:
        """
        Process a CEO directive end-to-end.

        JARVIS will autonomously plan, delegate to specialists, and synthesise
        a final executive briefing.
        """
        print(f"\n{'='*60}")
        print(f"[JARVIS] Received directive: {directive[:80]}...")
        print(f"{'='*60}\n")

        self._history.append({"role": "user", "content": directive})

        messages = list(self._history)

        while True:
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=8096,
                thinking={"type": "adaptive"},
                system=self._system_prompt(),
                tools=JARVIS_TOOLS,
                messages=messages,
            )

            # Collect text and tool calls from this turn
            text_out = ""
            tool_calls = []
            for block in response.content:
                if block.type == "text":
                    text_out += block.text
                elif block.type == "tool_use":
                    tool_calls.append(block)

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn" or not tool_calls:
                # Final answer — save to history and return
                self._history.append(
                    {"role": "assistant", "content": response.content}
                )
                if text_out:
                    print(f"\n[JARVIS] Final Report:\n{text_out}")
                return text_out

            # Execute each tool call (agent delegation)
            tool_results = []
            for tc in tool_calls:
                result = self._dispatch(tc.name, tc.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": json.dumps(result) if not isinstance(result, str) else result,
                })
                print(f"  ✓ {tc.name} completed")

            messages.append({"role": "user", "content": tool_results})

    def _dispatch(self, tool_name: str, tool_input: dict) -> Any:
        """Route a tool call to the appropriate agent."""
        if tool_name == "call_council":
            verdict = self._council.deliberate(tool_input["proposal"])
            return {
                "growth": verdict.growth_view,
                "retention": verdict.retention_view,
                "skeptic": verdict.skeptic_view,
                "consensus": verdict.consensus,
            }

        if tool_name == "call_oracle":
            return consult_oracle(
                question=tool_input["question"],
                context=tool_input.get("context", ""),
            )

        # Pattern: "call_atlas" → agents["atlas"]
        agent_key = tool_name.replace("call_", "")
        if agent_key in self._agents:
            agent = self._agents[agent_key]
            print(f"\n  → Delegating to {agent.name}...")
            return agent.run(tool_input["task"])

        return {"error": f"Unknown tool: {tool_name}"}

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are JARVIS, Chief Strategy Officer and master orchestrator. "
            "The CEO gives you high-level directives; you turn them into "
            "coordinated multi-agent execution.\n\n"
            "Your process:\n"
            "1. **Analyse** the directive — what's the goal? What's needed?\n"
            "2. **Plan** — identify which specialists need to be involved and in "
            "what order (some tasks are parallel, some sequential).\n"
            "3. **Delegate** — call each agent with a precise, scoped task.\n"
            "4. **Synthesise** — combine outputs into a coherent executive brief.\n\n"
            "Rules:\n"
            "- Only call Council for genuinely strategic decisions (not operational).\n"
            "- Only call ORACLE for the hardest, most consequential questions.\n"
            "- Be efficient: don't call agents you don't need.\n"
            "- Your final output is an executive summary for the CEO — clear, "
            "actionable, and concise."
        )

    def reset(self) -> None:
        """Clear conversation history (start a new session)."""
        self._history = []
        for agent in self._agents.values():
            agent.reset()

"""
Base agent class — every specialist and orchestrator inherits from this.

Pattern: each Agent wraps a Claude API call with:
  - a fixed system prompt defining its persona and expertise
  - a tool set restricting what it can do
  - adaptive thinking for complex reasoning
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import anthropic

client = anthropic.Anthropic()

# Default model for all agents. Swap to claude-sonnet-4-6 for cheaper sub-agents.
STRONG_MODEL = "claude-opus-4-6"
FAST_MODEL = "claude-sonnet-4-6"


@dataclass
class AgentMessage:
    role: str          # "user" | "assistant"
    content: str | list[dict]
    agent_name: str = ""


@dataclass
class Agent:
    """
    A single AI agent with a persona, tools, and conversation memory.

    Usage:
        agent = Agent(name="ATLAS", system_prompt="You are a research analyst...",
                      tools=[web_search_tool], model=STRONG_MODEL)
        response = agent.run("Find the latest AI news")
    """
    name: str
    system_prompt: str
    tools: list[dict] = field(default_factory=list)
    model: str = STRONG_MODEL
    history: list[dict] = field(default_factory=list)
    use_thinking: bool = True

    def run(self, user_message: str, *, fresh: bool = False) -> str:
        """
        Send a message to this agent and return its text response.

        Args:
            user_message: The task or question.
            fresh: If True, clears conversation history first (stateless call).
        """
        if fresh:
            self.history = []

        self.history.append({"role": "user", "content": user_message})

        params: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 8096,
            "system": self.system_prompt,
            "messages": self.history,
        }

        if self.use_thinking:
            params["thinking"] = {"type": "adaptive"}

        if self.tools:
            params["tools"] = self.tools

        # Agentic loop: keep going until no more tool calls
        while True:
            response = client.messages.create(**params)

            # Collect text output
            text_out = ""
            tool_calls = []
            for block in response.content:
                if block.type == "text":
                    text_out += block.text
                elif block.type == "tool_use":
                    tool_calls.append(block)

            if response.stop_reason == "end_turn" or not tool_calls:
                # Append assistant turn to history
                self.history.append({
                    "role": "assistant",
                    "content": response.content,
                })
                return text_out

            # Execute tool calls and feed results back
            self.history.append({
                "role": "assistant",
                "content": response.content,
            })

            tool_results = []
            for tc in tool_calls:
                result = self._execute_tool(tc.name, tc.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": json.dumps(result),
                })

            self.history.append({"role": "user", "content": tool_results})
            params["messages"] = self.history

    def _execute_tool(self, name: str, input_data: dict) -> Any:
        """Override in subclasses to provide real tool implementations."""
        return {"error": f"Tool '{name}' not implemented on agent '{self.name}'"}

    def reset(self) -> None:
        self.history = []

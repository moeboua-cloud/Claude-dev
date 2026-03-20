"""LLM provider abstraction layer - supports multiple model providers."""

from abc import ABC, abstractmethod
from typing import Any

from app.core.config import get_settings


class BaseLLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[dict], tools: list[dict] | None = None) -> dict[str, Any]:
        """Send a completion request to the LLM."""
        ...

    @abstractmethod
    async def complete_with_tools(
        self, messages: list[dict], tools: list[dict]
    ) -> dict[str, Any]:
        """Send a completion request with tool/function calling."""
        ...


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for local development and testing.

    Uses pattern matching on the input to generate realistic responses
    without requiring an actual LLM API call.
    """

    async def complete(self, messages: list[dict], tools: list[dict] | None = None) -> dict[str, Any]:
        last_message = messages[-1]["content"] if messages else ""
        return {
            "content": self._generate_mock_response(last_message),
            "model": "mock-llm",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
        }

    async def complete_with_tools(
        self, messages: list[dict], tools: list[dict]
    ) -> dict[str, Any]:
        last_message = messages[-1]["content"] if messages else ""
        intent = self._classify_intent(last_message)

        if intent == "lookup_user":
            return {
                "tool_calls": [{"name": "lookup_user", "arguments": {"query": last_message}}],
                "content": None,
            }
        elif intent == "compare_access":
            return {
                "tool_calls": [{"name": "compare_access", "arguments": {"query": last_message}}],
                "content": None,
            }
        elif intent == "explain_access":
            return {
                "tool_calls": [{"name": "explain_access", "arguments": {"query": last_message}}],
                "content": None,
            }
        elif intent == "recommend":
            return {
                "tool_calls": [{"name": "generate_recommendations", "arguments": {"query": last_message}}],
                "content": None,
            }

        return {"content": self._generate_mock_response(last_message), "tool_calls": None}

    def _classify_intent(self, message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ["why does", "why doesn't", "why can't", "explain why", "missing"]):
            return "explain_access"
        if any(w in msg for w in ["compare", "baseline", "expected", "persona"]):
            return "compare_access"
        if any(w in msg for w in ["recommend", "cleanup", "excess", "remove", "remediat"]):
            return "recommend"
        if any(w in msg for w in ["who is", "find user", "search", "look up", "show me"]):
            return "lookup_user"
        return "general"

    def _generate_mock_response(self, message: str) -> str:
        return (
            "Based on my analysis of the IAM data, I can provide the following insights. "
            "Please use the structured evidence and recommendations provided for detailed information."
        )


class OpenAIProvider(BaseLLMProvider):
    """OpenAI-compatible LLM provider. TODO: Production implementation."""

    def __init__(self):
        self.settings = get_settings()

    async def complete(self, messages: list[dict], tools: list[dict] | None = None) -> dict[str, Any]:
        # TODO: Implement with openai client
        raise NotImplementedError("OpenAI provider requires IAM_LLM_API_KEY configuration")

    async def complete_with_tools(self, messages: list[dict], tools: list[dict]) -> dict[str, Any]:
        raise NotImplementedError("OpenAI provider requires IAM_LLM_API_KEY configuration")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider. TODO: Production implementation."""

    def __init__(self):
        self.settings = get_settings()

    async def complete(self, messages: list[dict], tools: list[dict] | None = None) -> dict[str, Any]:
        raise NotImplementedError("Anthropic provider requires IAM_LLM_API_KEY configuration")

    async def complete_with_tools(self, messages: list[dict], tools: list[dict]) -> dict[str, Any]:
        raise NotImplementedError("Anthropic provider requires IAM_LLM_API_KEY configuration")


def get_llm_provider() -> BaseLLMProvider:
    settings = get_settings()
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    elif settings.llm_provider == "openai":
        return OpenAIProvider()
    elif settings.llm_provider == "anthropic":
        return AnthropicProvider()
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

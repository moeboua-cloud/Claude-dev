"""Tests for the IAM agent intent classification."""

import pytest
from app.agent.iam_agent import IAMAgent


def test_intent_classification():
    """Test that the agent correctly classifies user intents."""
    # We test the _classify_intent method directly
    agent_cls = IAMAgent.__new__(IAMAgent)

    assert agent_cls._classify_intent("Why does Sarah not have Epic access?") == "explain_access"
    assert agent_cls._classify_intent("Why doesn't John have Jira?") == "explain_access"
    assert agent_cls._classify_intent("Compare David's access to baseline") == "compare_access"
    assert agent_cls._classify_intent("Show me what access this user should have") == "compare_access"
    assert agent_cls._classify_intent("Recommend cleanup for Bob") == "recommend"
    assert agent_cls._classify_intent("Find excess entitlements") == "recommend"
    assert agent_cls._classify_intent("Who is Sarah Chen?") == "lookup_user"
    assert agent_cls._classify_intent("Search for EMP001") == "lookup_user"
    assert agent_cls._classify_intent("What changed after the move?") == "mover_analysis"
    assert agent_cls._classify_intent("Show audit timeline") == "audit_query"


def test_llm_provider_mock():
    """Test that the mock LLM provider works."""
    from app.agent.llm_provider import MockLLMProvider

    provider = MockLLMProvider()
    assert provider._classify_intent("Why does Sarah not have Epic?") == "explain_access"
    assert provider._classify_intent("Compare baseline") == "compare_access"
    assert provider._classify_intent("Recommend cleanup") == "recommend"

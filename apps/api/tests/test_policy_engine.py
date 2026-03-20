"""Tests for the deterministic policy engine."""

import pytest
from app.engine.policy_engine import PolicyEngine


@pytest.mark.asyncio
async def test_high_risk_requires_approval(db_session):
    engine = PolicyEngine(db_session)
    context = {
        "action": "add",
        "risk_level": "high",
        "is_privileged": False,
        "worker_type": "employee",
    }
    results = await engine.evaluate_action(context)
    approval_results = [r for r in results if r["result"] == "require_approval"]
    assert len(approval_results) > 0, "High-risk actions should require approval"


@pytest.mark.asyncio
async def test_contractor_privileged_denied(db_session):
    engine = PolicyEngine(db_session)
    context = {
        "action": "add",
        "risk_level": "high",
        "is_privileged": True,
        "worker_type": "contractor",
    }
    results = await engine.evaluate_action(context)
    denied = [r for r in results if r["result"] == "deny"]
    assert len(denied) > 0, "Contractors should be denied privileged access"


@pytest.mark.asyncio
async def test_low_risk_removal_allowed(db_session):
    engine = PolicyEngine(db_session)
    context = {
        "action": "remove",
        "risk_level": "low",
        "is_privileged": False,
        "worker_type": "employee",
    }
    results = await engine.evaluate_action(context)
    allowed = [r for r in results if r["result"] == "allow"]
    assert len(allowed) > 0, "Low-risk removals should be auto-allowed"


@pytest.mark.asyncio
async def test_risk_classification(db_session):
    engine = PolicyEngine(db_session)
    assert await engine.classify_risk("PAM-ServerAdmins", False, "add") == "high"
    assert await engine.classify_risk("GRP-DomainAdmins", False, "add") == "high"
    assert await engine.classify_risk("APP-Jira-Users", False, "add") == "medium"
    assert await engine.classify_risk("DL-AllEmployees", False, "add") == "low"
    assert await engine.classify_risk("PAM-DBA", True, "add") == "critical"

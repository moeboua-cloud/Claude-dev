"""Tests for mock connectors."""

import pytest
from app.connectors.mock_workday import MockWorkdayConnector
from app.connectors.mock_ad import MockADConnector
from app.connectors.mock_entra import MockEntraConnector


@pytest.mark.asyncio
async def test_workday_fetch_users():
    connector = MockWorkdayConnector()
    users = await connector.fetch_users()
    assert len(users) > 0
    assert all("employee_id" in u for u in users)
    assert all("job_family" in u for u in users)


@pytest.mark.asyncio
async def test_workday_fetch_user():
    connector = MockWorkdayConnector()
    user = await connector.fetch_user("EMP001")
    assert user is not None
    assert user["first_name"] == "Sarah"
    assert user["job_family"] == "Finance"


@pytest.mark.asyncio
async def test_workday_lifecycle():
    connector = MockWorkdayConnector()
    events = await connector.fetch_worker_lifecycle("EMP004")
    assert len(events) > 0
    assert events[0]["event_type"] == "move"


@pytest.mark.asyncio
async def test_ad_groups():
    connector = MockADConnector()
    groups = await connector.fetch_groups()
    assert len(groups) > 0
    privileged = [g for g in groups if g["is_privileged"]]
    assert len(privileged) > 0


@pytest.mark.asyncio
async def test_ad_user_memberships():
    connector = MockADConnector()
    memberships = await connector.fetch_user_memberships("EMP002")
    group_names = [g["name"] for g in memberships]
    assert "PAM-ServerAdmins" in group_names
    assert "GRP-DomainAdmins" in group_names  # Excess access scenario


@pytest.mark.asyncio
async def test_ad_mover_stale_access():
    """David Kim (EMP004) should still have old finance groups after move."""
    connector = MockADConnector()
    memberships = await connector.fetch_user_memberships("EMP004")
    group_names = [g["name"] for g in memberships]
    assert "GRP-Finance-Users" in group_names  # Stale
    assert "GRP-Engineering-Users" in group_names  # New


@pytest.mark.asyncio
async def test_ad_new_hire_missing_access():
    """Priya Patel (EMP007) new hire should have minimal access."""
    connector = MockADConnector()
    memberships = await connector.fetch_user_memberships("EMP007")
    group_names = [g["name"] for g in memberships]
    assert "GRP-Clinical-Users" not in group_names  # Missing baseline
    assert "APP-Epic-ClinicalUser" not in group_names  # Missing baseline


@pytest.mark.asyncio
async def test_entra_app_assignments():
    connector = MockEntraConnector()
    apps = await connector.fetch_user_app_assignments("EMP001")
    app_names = [a["name"] for a in apps]
    assert "Microsoft 365" in app_names
    assert "SAP S/4HANA" in app_names

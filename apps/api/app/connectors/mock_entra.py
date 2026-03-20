"""Mock Microsoft Entra ID connector for cloud identity and app assignments."""

from typing import Any

from app.connectors.base import BaseDirectoryConnector

MOCK_ENTRA_APPS = [
    {"app_id": "app-m365", "name": "Microsoft 365", "type": "saas", "sso_enabled": True},
    {"app_id": "app-teams", "name": "Microsoft Teams", "type": "saas", "sso_enabled": True},
    {"app_id": "app-salesforce", "name": "Salesforce", "type": "saas", "sso_enabled": True},
    {"app_id": "app-servicenow", "name": "ServiceNow", "type": "saas", "sso_enabled": True},
    {"app_id": "app-github", "name": "GitHub Enterprise", "type": "saas", "sso_enabled": True},
    {"app_id": "app-epic", "name": "Epic EHR", "type": "on_prem", "sso_enabled": False},
    {"app_id": "app-sap", "name": "SAP S/4HANA", "type": "hybrid", "sso_enabled": True},
    {"app_id": "app-workday", "name": "Workday", "type": "saas", "sso_enabled": True},
    {"app_id": "app-jira", "name": "Jira / Atlassian", "type": "saas", "sso_enabled": True},
    {"app_id": "app-slack", "name": "Slack", "type": "saas", "sso_enabled": True},
]

MOCK_ENTRA_APP_ASSIGNMENTS: dict[str, list[str]] = {
    "EMP001": ["app-m365", "app-teams", "app-sap", "app-servicenow", "app-slack"],
    "EMP002": ["app-m365", "app-teams", "app-jira", "app-servicenow", "app-github", "app-slack"],
    "EMP003": ["app-m365", "app-teams", "app-epic", "app-servicenow", "app-slack"],
    "EMP004": ["app-m365", "app-teams", "app-sap", "app-jira", "app-github", "app-servicenow", "app-slack"],
    "EMP005": ["app-m365", "app-teams", "app-workday", "app-servicenow", "app-slack"],
    "EMP006": ["app-m365", "app-teams", "app-servicenow", "app-slack"],
    "EMP007": ["app-m365", "app-teams", "app-slack"],  # Missing Epic for new nurse
    "EMP008": ["app-jira", "app-github", "app-slack"],  # Contractor - limited
    "EMP010": ["app-m365", "app-teams", "app-sap", "app-servicenow", "app-salesforce", "app-slack"],
    "EMP011": ["app-m365", "app-teams", "app-jira", "app-github", "app-servicenow", "app-slack"],
}

MOCK_ENTRA_GROUPS = [
    {"name": "Entra-AllUsers", "type": "security", "source": "entra", "is_privileged": False, "risk_level": "low"},
    {"name": "Entra-M365-E3", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low"},
    {"name": "Entra-M365-E5", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low"},
    {"name": "Entra-ConditionalAccess-MFA", "type": "security", "source": "entra", "is_privileged": False, "risk_level": "low"},
    {"name": "Entra-GlobalAdmin", "type": "role", "source": "entra", "is_privileged": True, "risk_level": "critical"},
]


class MockEntraConnector(BaseDirectoryConnector):
    """Mock Entra ID connector."""

    async def test_connection(self) -> bool:
        return True

    async def fetch_users(self) -> list[dict[str, Any]]:
        return [
            {"employee_id": emp_id, "app_assignments": apps}
            for emp_id, apps in MOCK_ENTRA_APP_ASSIGNMENTS.items()
        ]

    async def fetch_user(self, identifier: str) -> dict[str, Any] | None:
        apps = MOCK_ENTRA_APP_ASSIGNMENTS.get(identifier)
        if apps is None:
            return None
        return {"employee_id": identifier, "app_assignments": apps}

    async def fetch_groups(self) -> list[dict[str, Any]]:
        return MOCK_ENTRA_GROUPS

    async def fetch_group_members(self, group_id: str) -> list[str]:
        return list(MOCK_ENTRA_APP_ASSIGNMENTS.keys())  # simplified

    async def fetch_user_memberships(self, user_id: str) -> list[dict[str, Any]]:
        apps = MOCK_ENTRA_APP_ASSIGNMENTS.get(user_id, [])
        return [a for a in MOCK_ENTRA_APPS if a["app_id"] in apps]

    async def fetch_app_catalog(self) -> list[dict[str, Any]]:
        return MOCK_ENTRA_APPS

    async def fetch_user_app_assignments(self, user_id: str) -> list[dict[str, Any]]:
        app_ids = MOCK_ENTRA_APP_ASSIGNMENTS.get(user_id, [])
        return [a for a in MOCK_ENTRA_APPS if a["app_id"] in app_ids]

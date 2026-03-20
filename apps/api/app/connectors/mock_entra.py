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
    {"app_id": "app-powerbi", "name": "Power BI", "type": "saas", "sso_enabled": True},
    {"app_id": "app-sharepoint", "name": "SharePoint Online", "type": "saas", "sso_enabled": True},
    {"app_id": "app-exchange", "name": "Exchange Online", "type": "saas", "sso_enabled": True},
    {"app_id": "app-onedrive", "name": "OneDrive for Business", "type": "saas", "sso_enabled": True},
]

MOCK_ENTRA_APP_ASSIGNMENTS: dict[str, list[str]] = {
    "EMP001": ["app-m365", "app-teams", "app-sap", "app-servicenow", "app-slack", "app-sharepoint", "app-exchange", "app-onedrive"],
    "EMP002": ["app-m365", "app-teams", "app-jira", "app-servicenow", "app-github", "app-slack", "app-sharepoint", "app-exchange", "app-onedrive"],
    "EMP003": ["app-m365", "app-teams", "app-epic", "app-servicenow", "app-slack", "app-sharepoint", "app-exchange", "app-onedrive"],
    "EMP004": ["app-m365", "app-teams", "app-sap", "app-jira", "app-github", "app-servicenow", "app-slack", "app-sharepoint", "app-exchange", "app-onedrive"],
    "EMP005": ["app-m365", "app-teams", "app-workday", "app-servicenow", "app-slack", "app-sharepoint", "app-exchange", "app-onedrive"],
    "EMP006": ["app-m365", "app-teams", "app-servicenow", "app-slack", "app-sharepoint", "app-exchange", "app-onedrive"],
    "EMP007": ["app-m365", "app-teams", "app-slack", "app-sharepoint", "app-exchange", "app-onedrive"],  # Missing Epic for new nurse
    "EMP008": ["app-jira", "app-github", "app-slack"],  # Contractor - limited, no M365 license
    "EMP010": ["app-m365", "app-teams", "app-sap", "app-servicenow", "app-salesforce", "app-slack", "app-powerbi", "app-sharepoint", "app-exchange", "app-onedrive"],
    "EMP011": ["app-m365", "app-teams", "app-jira", "app-github", "app-servicenow", "app-slack", "app-powerbi", "app-sharepoint", "app-exchange", "app-onedrive"],
}

MOCK_ENTRA_GROUPS = [
    {"name": "Entra-AllUsers", "type": "security", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "security_group"},
    {"name": "Entra-ConditionalAccess-MFA", "type": "security", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "security_group"},

    # === Licenses ===
    {"name": "LIC-M365-E3", "display_name": "Microsoft 365 E3 License", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "license"},
    {"name": "LIC-M365-E5", "display_name": "Microsoft 365 E5 License", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "license"},
    {"name": "LIC-PowerBI-Pro", "display_name": "Power BI Pro License", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "license"},
    {"name": "LIC-Visio-Plan2", "display_name": "Visio Plan 2 License", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "license"},
    {"name": "LIC-Project-Plan3", "display_name": "Project Plan 3 License", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "license"},
    {"name": "LIC-EMS-E5", "display_name": "Enterprise Mobility + Security E5", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "license"},
    {"name": "LIC-Copilot", "display_name": "Microsoft 365 Copilot License", "type": "license", "source": "entra", "is_privileged": False, "risk_level": "low", "category": "license"},

    # === Privileged Entra Roles ===
    {"name": "Entra-GlobalAdmin", "display_name": "Entra Global Administrator", "type": "role", "source": "entra", "is_privileged": True, "risk_level": "critical", "category": "privileged_access"},
    {"name": "Entra-UserAdmin", "display_name": "Entra User Administrator", "type": "role", "source": "entra", "is_privileged": True, "risk_level": "high", "category": "privileged_access"},
    {"name": "Entra-SecurityAdmin", "display_name": "Entra Security Administrator", "type": "role", "source": "entra", "is_privileged": True, "risk_level": "high", "category": "privileged_access"},
    {"name": "Entra-ExchangeAdmin", "display_name": "Exchange Administrator", "type": "role", "source": "entra", "is_privileged": True, "risk_level": "high", "category": "privileged_access"},
    {"name": "Entra-SharePointAdmin", "display_name": "SharePoint Administrator", "type": "role", "source": "entra", "is_privileged": True, "risk_level": "high", "category": "privileged_access"},
    {"name": "Entra-IntuneAdmin", "display_name": "Intune Administrator", "type": "role", "source": "entra", "is_privileged": True, "risk_level": "high", "category": "privileged_access"},
]

# License assignments per user
MOCK_ENTRA_LICENSE_ASSIGNMENTS: dict[str, list[str]] = {
    "EMP001": ["LIC-M365-E3", "Entra-AllUsers", "Entra-ConditionalAccess-MFA"],
    "EMP002": ["LIC-M365-E5", "LIC-EMS-E5", "Entra-AllUsers", "Entra-ConditionalAccess-MFA", "Entra-UserAdmin"],
    "EMP003": ["LIC-M365-E3", "Entra-AllUsers", "Entra-ConditionalAccess-MFA"],
    "EMP004": ["LIC-M365-E3", "LIC-Visio-Plan2", "Entra-AllUsers", "Entra-ConditionalAccess-MFA"],
    "EMP005": ["LIC-M365-E3", "Entra-AllUsers", "Entra-ConditionalAccess-MFA"],
    "EMP006": ["LIC-M365-E5", "LIC-EMS-E5", "Entra-AllUsers", "Entra-ConditionalAccess-MFA", "Entra-SecurityAdmin"],
    "EMP007": ["LIC-M365-E3", "Entra-AllUsers", "Entra-ConditionalAccess-MFA"],
    "EMP008": [],  # Contractor - no Entra licenses
    "EMP010": ["LIC-M365-E5", "LIC-PowerBI-Pro", "LIC-Copilot", "Entra-AllUsers", "Entra-ConditionalAccess-MFA"],
    "EMP011": ["LIC-M365-E5", "LIC-PowerBI-Pro", "LIC-Project-Plan3", "LIC-Copilot", "Entra-AllUsers", "Entra-ConditionalAccess-MFA"],
}


class MockEntraConnector(BaseDirectoryConnector):
    """Mock Entra ID connector."""

    async def test_connection(self) -> bool:
        return True

    async def fetch_users(self) -> list[dict[str, Any]]:
        return [
            {
                "employee_id": emp_id,
                "app_assignments": apps,
                "entra_groups": MOCK_ENTRA_LICENSE_ASSIGNMENTS.get(emp_id, []),
            }
            for emp_id, apps in MOCK_ENTRA_APP_ASSIGNMENTS.items()
        ]

    async def fetch_user(self, identifier: str) -> dict[str, Any] | None:
        apps = MOCK_ENTRA_APP_ASSIGNMENTS.get(identifier)
        if apps is None:
            return None
        return {
            "employee_id": identifier,
            "app_assignments": apps,
            "entra_groups": MOCK_ENTRA_LICENSE_ASSIGNMENTS.get(identifier, []),
        }

    async def fetch_groups(self) -> list[dict[str, Any]]:
        return MOCK_ENTRA_GROUPS

    async def fetch_group_members(self, group_id: str) -> list[str]:
        return [
            emp_id for emp_id, groups in MOCK_ENTRA_LICENSE_ASSIGNMENTS.items()
            if group_id in groups
        ]

    async def fetch_user_memberships(self, user_id: str) -> list[dict[str, Any]]:
        group_names = MOCK_ENTRA_LICENSE_ASSIGNMENTS.get(user_id, [])
        return [g for g in MOCK_ENTRA_GROUPS if g["name"] in group_names]

    async def fetch_app_catalog(self) -> list[dict[str, Any]]:
        return MOCK_ENTRA_APPS

    async def fetch_user_app_assignments(self, user_id: str) -> list[dict[str, Any]]:
        app_ids = MOCK_ENTRA_APP_ASSIGNMENTS.get(user_id, [])
        return [a for a in MOCK_ENTRA_APPS if a["app_id"] in app_ids]

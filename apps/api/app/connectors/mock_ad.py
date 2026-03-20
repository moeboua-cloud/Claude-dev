"""Mock Active Directory connector with realistic group and membership data."""

from typing import Any

from app.connectors.base import BaseDirectoryConnector

MOCK_AD_GROUPS = [
    # Standard department groups
    {"name": "GRP-Finance-Users", "display_name": "Finance Department Users", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "low"},
    {"name": "GRP-IT-Users", "display_name": "IT Department Users", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "low"},
    {"name": "GRP-Clinical-Users", "display_name": "Clinical Department Users", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "low"},
    {"name": "GRP-HR-Users", "display_name": "HR Department Users", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "low"},
    {"name": "GRP-Engineering-Users", "display_name": "Engineering Department Users", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "low"},
    # Application access groups
    {"name": "APP-Epic-ClinicalUser", "display_name": "Epic Clinical User Access", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "medium"},
    {"name": "APP-Epic-Admin", "display_name": "Epic Admin Access", "type": "security", "source": "ad", "is_privileged": True, "risk_level": "high"},
    {"name": "APP-SAP-Users", "display_name": "SAP Standard Users", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "medium"},
    {"name": "APP-SAP-FinanceAdmin", "display_name": "SAP Finance Admin", "type": "security", "source": "ad", "is_privileged": True, "risk_level": "high"},
    {"name": "APP-Jira-Users", "display_name": "Jira Standard Users", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "low"},
    {"name": "APP-GitHub-Developers", "display_name": "GitHub Developer Access", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "medium"},
    {"name": "APP-Workday-HRAdmin", "display_name": "Workday HR Admin", "type": "security", "source": "ad", "is_privileged": True, "risk_level": "high"},
    {"name": "APP-ServiceNow-Users", "display_name": "ServiceNow Users", "type": "security", "source": "ad", "is_privileged": False, "risk_level": "low"},
    # Privileged groups
    {"name": "PAM-ServerAdmins", "display_name": "Server Administrators (PAM)", "type": "security", "source": "ad", "is_privileged": True, "risk_level": "critical"},
    {"name": "PAM-DBA", "display_name": "Database Administrators (PAM)", "type": "security", "source": "ad", "is_privileged": True, "risk_level": "critical"},
    {"name": "GRP-DomainAdmins", "display_name": "Domain Administrators", "type": "security", "source": "ad", "is_privileged": True, "risk_level": "critical"},
    # Distribution groups
    {"name": "DL-AllEmployees", "display_name": "All Employees", "type": "distribution", "source": "ad", "is_privileged": False, "risk_level": "low"},
    {"name": "DL-Finance-Team", "display_name": "Finance Team DL", "type": "distribution", "source": "ad", "is_privileged": False, "risk_level": "low"},
    {"name": "DL-IT-Team", "display_name": "IT Team DL", "type": "distribution", "source": "ad", "is_privileged": False, "risk_level": "low"},
]

# Intentional access patterns including anomalies
MOCK_AD_MEMBERSHIPS: dict[str, list[str]] = {
    # Sarah Chen (Finance) - has proper finance access
    "EMP001": [
        "GRP-Finance-Users", "DL-Finance-Team", "DL-AllEmployees",
        "APP-SAP-Users", "APP-ServiceNow-Users",
    ],
    # John Smith (IT SysAdmin) - has proper IT access + excess privileged group
    "EMP002": [
        "GRP-IT-Users", "DL-IT-Team", "DL-AllEmployees",
        "APP-Jira-Users", "APP-ServiceNow-Users",
        "PAM-ServerAdmins",
        "GRP-DomainAdmins",  # EXCESS: should not have Domain Admin
    ],
    # Maria Garcia (Clinical Informatics) - proper clinical access
    "EMP003": [
        "GRP-Clinical-Users", "DL-AllEmployees",
        "APP-Epic-ClinicalUser", "APP-ServiceNow-Users",
    ],
    # David Kim (Mover: Finance -> IT) - still has old finance groups
    "EMP004": [
        "GRP-Finance-Users",  # STALE: from old role
        "DL-Finance-Team",    # STALE: from old role
        "APP-SAP-Users",      # STALE: from old role
        "GRP-Engineering-Users",  # NEW: correct for new role
        "DL-IT-Team",            # NEW: correct for new role
        "APP-Jira-Users",        # NEW: correct for new role
        "APP-GitHub-Developers", # NEW: correct for new role
        "DL-AllEmployees",
        "APP-ServiceNow-Users",
    ],
    # Lisa Johnson (HR) - proper HR access + exception privileged access
    "EMP005": [
        "GRP-HR-Users", "DL-AllEmployees",
        "APP-Workday-HRAdmin",  # EXCEPTION: privileged but approved
        "APP-ServiceNow-Users",
    ],
    # James Wilson (SecOps, new-ish) - missing some expected groups
    "EMP006": [
        "GRP-IT-Users", "DL-IT-Team", "DL-AllEmployees",
        "APP-ServiceNow-Users",
        # MISSING: should have APP-Jira-Users for SecOps
        # MISSING: should have PAM-ServerAdmins (read-only) for SecOps
    ],
    # Priya Patel (New hire nurse) - missing baseline clinical access
    "EMP007": [
        "DL-AllEmployees",
        # MISSING: GRP-Clinical-Users
        # MISSING: APP-Epic-ClinicalUser
    ],
    # Bob External (Contractor) - limited access
    "EMP008": [
        "GRP-Engineering-Users",
        "APP-Jira-Users",
        "APP-GitHub-Developers",
        "PAM-ServerAdmins",  # EXCESS: contractor should not have PAM access
    ],
    # Michael Torres (Finance Director)
    "EMP010": [
        "GRP-Finance-Users", "DL-Finance-Team", "DL-AllEmployees",
        "APP-SAP-Users", "APP-SAP-FinanceAdmin",
        "APP-ServiceNow-Users",
    ],
    # Rachel Wong (VP Engineering)
    "EMP011": [
        "GRP-IT-Users", "GRP-Engineering-Users", "DL-IT-Team", "DL-AllEmployees",
        "APP-Jira-Users", "APP-GitHub-Developers",
        "APP-ServiceNow-Users",
    ],
}


class MockADConnector(BaseDirectoryConnector):
    """Mock Active Directory connector."""

    async def test_connection(self) -> bool:
        return True

    async def fetch_users(self) -> list[dict[str, Any]]:
        # AD returns user objects with sAMAccountName, UPN, etc.
        users = []
        for emp_id, groups in MOCK_AD_MEMBERSHIPS.items():
            users.append({
                "employee_id": emp_id,
                "sam_account_name": emp_id.lower(),
                "groups": groups,
            })
        return users

    async def fetch_user(self, identifier: str) -> dict[str, Any] | None:
        groups = MOCK_AD_MEMBERSHIPS.get(identifier, [])
        if not groups and identifier not in MOCK_AD_MEMBERSHIPS:
            return None
        return {"employee_id": identifier, "sam_account_name": identifier.lower(), "groups": groups}

    async def fetch_groups(self) -> list[dict[str, Any]]:
        return MOCK_AD_GROUPS

    async def fetch_group_members(self, group_id: str) -> list[str]:
        return [emp for emp, groups in MOCK_AD_MEMBERSHIPS.items() if group_id in groups]

    async def fetch_user_memberships(self, user_id: str) -> list[dict[str, Any]]:
        member_group_names = MOCK_AD_MEMBERSHIPS.get(user_id, [])
        return [g for g in MOCK_AD_GROUPS if g["name"] in member_group_names]

"""Mock Workday / HRIS connector with realistic sample data."""

from typing import Any
from datetime import datetime, timedelta, UTC

from app.connectors.base import BaseHRConnector

# Realistic sample HR data
MOCK_WORKERS = [
    {
        "employee_id": "EMP001",
        "email": "sarah.chen@company.com",
        "first_name": "Sarah",
        "last_name": "Chen",
        "display_name": "Sarah Chen",
        "job_title": "Senior Financial Analyst",
        "job_family": "Finance",
        "sub_job_family": "Financial Planning & Analysis",
        "department": "Corporate Finance",
        "cost_center": "CC-FIN-100",
        "legal_entity": "Company Corp US",
        "region": "US-East",
        "location": "New York",
        "manager_employee_id": "EMP010",
        "worker_type": "employee",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=730)).isoformat(),
    },
    {
        "employee_id": "EMP002",
        "email": "john.smith@company.com",
        "first_name": "John",
        "last_name": "Smith",
        "display_name": "John Smith",
        "job_title": "IT Systems Administrator",
        "job_family": "Information Technology",
        "sub_job_family": "Infrastructure",
        "department": "IT Operations",
        "cost_center": "CC-IT-200",
        "legal_entity": "Company Corp US",
        "region": "US-West",
        "location": "San Francisco",
        "manager_employee_id": "EMP011",
        "worker_type": "employee",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=1095)).isoformat(),
    },
    {
        "employee_id": "EMP003",
        "email": "maria.garcia@company.com",
        "first_name": "Maria",
        "last_name": "Garcia",
        "display_name": "Maria Garcia",
        "job_title": "Clinical Applications Specialist",
        "job_family": "Clinical",
        "sub_job_family": "Clinical Informatics",
        "department": "Health Informatics",
        "cost_center": "CC-CLI-300",
        "legal_entity": "Company Health US",
        "region": "US-East",
        "location": "Boston",
        "manager_employee_id": "EMP012",
        "worker_type": "employee",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=365)).isoformat(),
    },
    {
        "employee_id": "EMP004",
        "email": "david.kim@company.com",
        "first_name": "David",
        "last_name": "Kim",
        "display_name": "David Kim",
        "job_title": "Software Engineer",
        "job_family": "Information Technology",
        "sub_job_family": "Software Engineering",
        "department": "Product Engineering",
        "cost_center": "CC-ENG-400",
        "legal_entity": "Company Corp US",
        "region": "US-West",
        "location": "San Francisco",
        "manager_employee_id": "EMP011",
        "worker_type": "employee",
        "lifecycle_state": "mover",  # Recently moved from Finance to IT
        "hire_date": (datetime.now(UTC) - timedelta(days=900)).isoformat(),
        "_previous_department": "Corporate Finance",
        "_previous_job_family": "Finance",
        "_previous_cost_center": "CC-FIN-100",
        "_move_date": (datetime.now(UTC) - timedelta(days=14)).isoformat(),
    },
    {
        "employee_id": "EMP005",
        "email": "lisa.johnson@company.com",
        "first_name": "Lisa",
        "last_name": "Johnson",
        "display_name": "Lisa Johnson",
        "job_title": "HR Business Partner",
        "job_family": "Human Resources",
        "sub_job_family": "HR Business Partner",
        "department": "Human Resources",
        "cost_center": "CC-HR-500",
        "legal_entity": "Company Corp US",
        "region": "US-East",
        "location": "New York",
        "manager_employee_id": "EMP013",
        "worker_type": "employee",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=1460)).isoformat(),
    },
    {
        "employee_id": "EMP006",
        "email": "james.wilson@company.com",
        "first_name": "James",
        "last_name": "Wilson",
        "display_name": "James Wilson",
        "job_title": "Security Operations Analyst",
        "job_family": "Information Technology",
        "sub_job_family": "Security Operations",
        "department": "Information Security",
        "cost_center": "CC-SEC-600",
        "legal_entity": "Company Corp US",
        "region": "US-East",
        "location": "New York",
        "manager_employee_id": "EMP014",
        "worker_type": "employee",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=200)).isoformat(),
    },
    {
        "employee_id": "EMP007",
        "email": "priya.patel@company.com",
        "first_name": "Priya",
        "last_name": "Patel",
        "display_name": "Priya Patel",
        "job_title": "Registered Nurse",
        "job_family": "Clinical",
        "sub_job_family": "Nursing",
        "department": "Nursing - ICU",
        "cost_center": "CC-NUR-700",
        "legal_entity": "Company Health US",
        "region": "US-East",
        "location": "Boston",
        "manager_employee_id": "EMP012",
        "worker_type": "employee",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=30)).isoformat(),  # New hire
    },
    {
        "employee_id": "EMP008",
        "email": "contractor.bob@vendor.com",
        "first_name": "Bob",
        "last_name": "External",
        "display_name": "Bob External (Contractor)",
        "job_title": "Contract Developer",
        "job_family": "Information Technology",
        "sub_job_family": "Software Engineering",
        "department": "Product Engineering",
        "cost_center": "CC-ENG-400",
        "legal_entity": "Company Corp US",
        "region": "US-West",
        "location": "Remote",
        "manager_employee_id": "EMP011",
        "worker_type": "contractor",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=60)).isoformat(),
    },
    # Managers
    {
        "employee_id": "EMP010",
        "email": "michael.torres@company.com",
        "first_name": "Michael",
        "last_name": "Torres",
        "display_name": "Michael Torres",
        "job_title": "Finance Director",
        "job_family": "Finance",
        "sub_job_family": "Finance Leadership",
        "department": "Corporate Finance",
        "cost_center": "CC-FIN-100",
        "legal_entity": "Company Corp US",
        "region": "US-East",
        "location": "New York",
        "manager_employee_id": "EMP020",
        "worker_type": "employee",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=2000)).isoformat(),
    },
    {
        "employee_id": "EMP011",
        "email": "rachel.wong@company.com",
        "first_name": "Rachel",
        "last_name": "Wong",
        "display_name": "Rachel Wong",
        "job_title": "VP of Engineering",
        "job_family": "Information Technology",
        "sub_job_family": "IT Leadership",
        "department": "Product Engineering",
        "cost_center": "CC-ENG-400",
        "legal_entity": "Company Corp US",
        "region": "US-West",
        "location": "San Francisco",
        "manager_employee_id": "EMP020",
        "worker_type": "employee",
        "lifecycle_state": "active",
        "hire_date": (datetime.now(UTC) - timedelta(days=1800)).isoformat(),
    },
]

MOCK_LIFECYCLE_EVENTS = [
    {
        "employee_id": "EMP004",
        "event_type": "move",
        "previous_state": {
            "department": "Corporate Finance",
            "job_family": "Finance",
            "job_title": "Financial Analyst",
            "cost_center": "CC-FIN-100",
        },
        "new_state": {
            "department": "Product Engineering",
            "job_family": "Information Technology",
            "job_title": "Software Engineer",
            "cost_center": "CC-ENG-400",
        },
        "effective_date": (datetime.now(UTC) - timedelta(days=14)).isoformat(),
    },
    {
        "employee_id": "EMP007",
        "event_type": "join",
        "previous_state": None,
        "new_state": {
            "department": "Nursing - ICU",
            "job_family": "Clinical",
            "job_title": "Registered Nurse",
        },
        "effective_date": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
    },
]


class MockWorkdayConnector(BaseHRConnector):
    """Mock HRIS connector simulating Workday API responses."""

    async def test_connection(self) -> bool:
        return True

    async def fetch_users(self) -> list[dict[str, Any]]:
        return MOCK_WORKERS

    async def fetch_user(self, identifier: str) -> dict[str, Any] | None:
        for w in MOCK_WORKERS:
            if w["employee_id"] == identifier or w["email"] == identifier:
                return w
        return None

    async def fetch_groups(self) -> list[dict[str, Any]]:
        # Workday doesn't have groups in the AD sense, return org units
        departments = {w["department"] for w in MOCK_WORKERS if w.get("department")}
        return [{"name": d, "type": "department"} for d in departments]

    async def fetch_group_members(self, group_id: str) -> list[str]:
        return [w["employee_id"] for w in MOCK_WORKERS if w.get("department") == group_id]

    async def fetch_worker_lifecycle(self, employee_id: str) -> list[dict[str, Any]]:
        return [e for e in MOCK_LIFECYCLE_EVENTS if e["employee_id"] == employee_id]

    async def fetch_org_structure(self) -> list[dict[str, Any]]:
        return [
            {"name": "Corporate Finance", "parent": "Finance Division", "head": "EMP010"},
            {"name": "Product Engineering", "parent": "Technology Division", "head": "EMP011"},
            {"name": "Health Informatics", "parent": "Clinical Division", "head": "EMP012"},
            {"name": "Human Resources", "parent": "People Division", "head": "EMP013"},
            {"name": "Information Security", "parent": "Technology Division", "head": "EMP014"},
        ]

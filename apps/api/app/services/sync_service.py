"""Sync service - ingests data from source connectors into normalized models."""

from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import User, UserLifecycleEvent, LifecycleState, WorkerType
from app.models.entitlement import Application, Group, Entitlement, UserEntitlement
from app.models.persona import Persona, PersonaMappingRule, PersonaEntitlement
from app.models.policy import PolicyRule
from app.connectors.registry import get_connector_registry
from app.engine.policy_engine import DEFAULT_POLICIES
from app.services.audit_service import AuditService


class SyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.registry = get_connector_registry()
        self.audit = AuditService(db)

    async def run_full_sync(self) -> dict[str, Any]:
        """Run a full sync from all source systems."""
        results = {}
        results["users"] = await self.sync_users()
        results["groups"] = await self.sync_groups()
        results["applications"] = await self.sync_applications()
        results["entitlements"] = await self.sync_entitlements()
        results["personas"] = await self.sync_personas()
        results["policies"] = await self.sync_policies()

        await self.audit.log(
            event_type="sync",
            actor="system",
            summary="Full sync completed",
            details=results,
        )
        return results

    async def sync_users(self) -> dict[str, int]:
        hr = self.registry.get_hr_connector()
        workers = await hr.fetch_users()

        created = 0
        updated = 0

        for w in workers:
            existing = await self.db.execute(
                select(User).where(User.employee_id == w["employee_id"])
            )
            user = existing.scalar_one_or_none()

            lifecycle_map = {v.value: v for v in LifecycleState}
            worker_type_map = {v.value: v for v in WorkerType}

            if user:
                # Update
                for field in ["display_name", "first_name", "last_name", "email", "job_title",
                              "job_family", "sub_job_family", "department", "cost_center",
                              "legal_entity", "region", "location", "manager_employee_id"]:
                    if field in w:
                        setattr(user, field, w[field])
                user.worker_type = worker_type_map.get(w.get("worker_type", "employee"), WorkerType.EMPLOYEE)
                user.lifecycle_state = lifecycle_map.get(w.get("lifecycle_state", "active"), LifecycleState.ACTIVE)
                user.last_synced_at = datetime.now(UTC)
                if w.get("hire_date"):
                    user.hire_date = datetime.fromisoformat(w["hire_date"])
                updated += 1
            else:
                user = User(
                    employee_id=w["employee_id"],
                    email=w["email"],
                    display_name=w["display_name"],
                    first_name=w["first_name"],
                    last_name=w["last_name"],
                    job_title=w.get("job_title"),
                    job_family=w.get("job_family"),
                    sub_job_family=w.get("sub_job_family"),
                    department=w.get("department"),
                    cost_center=w.get("cost_center"),
                    legal_entity=w.get("legal_entity"),
                    region=w.get("region"),
                    location=w.get("location"),
                    manager_employee_id=w.get("manager_employee_id"),
                    worker_type=worker_type_map.get(w.get("worker_type", "employee"), WorkerType.EMPLOYEE),
                    lifecycle_state=lifecycle_map.get(w.get("lifecycle_state", "active"), LifecycleState.ACTIVE),
                    hire_date=datetime.fromisoformat(w["hire_date"]) if w.get("hire_date") else None,
                    last_synced_at=datetime.now(UTC),
                )
                self.db.add(user)
                created += 1

        # Sync lifecycle events
        for w in workers:
            events = await hr.fetch_worker_lifecycle(w["employee_id"])
            for evt in events:
                user_result = await self.db.execute(
                    select(User).where(User.employee_id == evt["employee_id"])
                )
                user = user_result.scalar_one_or_none()
                if user:
                    existing_evt = await self.db.execute(
                        select(UserLifecycleEvent).where(
                            UserLifecycleEvent.user_id == user.id,
                            UserLifecycleEvent.event_type == evt["event_type"],
                        )
                    )
                    if not existing_evt.scalar_one_or_none():
                        self.db.add(UserLifecycleEvent(
                            user_id=user.id,
                            event_type=evt["event_type"],
                            previous_state=evt.get("previous_state"),
                            new_state=evt.get("new_state"),
                            effective_date=datetime.fromisoformat(evt["effective_date"]),
                        ))

        await self.db.flush()
        return {"created": created, "updated": updated}

    async def sync_groups(self) -> dict[str, int]:
        ad = self.registry.get_ad_connector()
        ad_groups = await ad.fetch_groups()

        created = 0
        for g in ad_groups:
            existing = await self.db.execute(select(Group).where(Group.name == g["name"]))
            if not existing.scalar_one_or_none():
                self.db.add(Group(
                    name=g["name"],
                    display_name=g.get("display_name"),
                    group_type=g["type"],
                    source=g["source"],
                    is_privileged=g.get("is_privileged", False),
                    risk_level=g.get("risk_level", "low"),
                ))
                created += 1

        await self.db.flush()
        return {"created": created}

    async def sync_applications(self) -> dict[str, int]:
        entra = self.registry.get_entra_connector()
        apps = await entra.fetch_app_catalog()

        created = 0
        for a in apps:
            existing = await self.db.execute(select(Application).where(Application.name == a["name"]))
            if not existing.scalar_one_or_none():
                self.db.add(Application(
                    name=a["name"],
                    app_type=a["type"],
                    sso_enabled=a.get("sso_enabled", False),
                ))
                created += 1

        await self.db.flush()
        return {"created": created}

    async def sync_entitlements(self) -> dict[str, int]:
        """Sync AD group memberships and app assignments as entitlements."""
        ad = self.registry.get_ad_connector()
        ad_groups = await ad.fetch_groups()

        # Ensure entitlement catalog entries for each group
        created_ents = 0
        for g in ad_groups:
            existing = await self.db.execute(
                select(Entitlement).where(Entitlement.source_identifier == g["name"])
            )
            if not existing.scalar_one_or_none():
                group_result = await self.db.execute(select(Group).where(Group.name == g["name"]))
                group = group_result.scalar_one_or_none()
                self.db.add(Entitlement(
                    name=g.get("display_name", g["name"]),
                    entitlement_type="group_membership",
                    source_system="ad",
                    source_identifier=g["name"],
                    group_id=group.id if group else None,
                    is_privileged=g.get("is_privileged", False),
                    risk_level=g.get("risk_level", "low"),
                ))
                created_ents += 1

        await self.db.flush()

        # Sync user-entitlement mappings from AD
        assigned = 0
        ad_users = await ad.fetch_users()
        for ad_user in ad_users:
            user_result = await self.db.execute(
                select(User).where(User.employee_id == ad_user["employee_id"])
            )
            user = user_result.scalar_one_or_none()
            if not user:
                continue

            for group_name in ad_user.get("groups", []):
                ent_result = await self.db.execute(
                    select(Entitlement).where(Entitlement.source_identifier == group_name)
                )
                ent = ent_result.scalar_one_or_none()
                if not ent:
                    continue

                existing_ue = await self.db.execute(
                    select(UserEntitlement).where(
                        UserEntitlement.user_id == user.id,
                        UserEntitlement.entitlement_id == ent.id,
                    )
                )
                if not existing_ue.scalar_one_or_none():
                    # Determine if this is an exception entitlement
                    is_exception = self._is_known_exception(user.employee_id, group_name)
                    self.db.add(UserEntitlement(
                        user_id=user.id,
                        entitlement_id=ent.id,
                        source="ad",
                        is_exception=is_exception,
                        exception_reason="Approved exception per IAM-2024-001" if is_exception else None,
                        exception_approved_by="iam_admin" if is_exception else None,
                        granted_at=datetime.now(UTC),
                    ))
                    assigned += 1

        await self.db.flush()
        return {"entitlements_created": created_ents, "assignments_created": assigned}

    def _is_known_exception(self, employee_id: str, group_name: str) -> bool:
        """Check if an entitlement is a known approved exception."""
        known_exceptions = {
            ("EMP005", "APP-Workday-HRAdmin"),  # Lisa has approved HR admin exception
        }
        return (employee_id, group_name) in known_exceptions

    async def sync_personas(self) -> dict[str, int]:
        """Seed persona definitions and mapping rules."""
        personas_data = [
            {
                "name": "Finance Analyst",
                "description": "Standard finance department analyst",
                "job_family": "Finance",
                "entitlements": [
                    {"type": "group_membership", "id": "GRP-Finance-Users", "name": "Finance Department Users", "required": True},
                    {"type": "group_membership", "id": "DL-Finance-Team", "name": "Finance Team DL", "required": False},
                    {"type": "group_membership", "id": "DL-AllEmployees", "name": "All Employees", "required": True},
                    {"type": "group_membership", "id": "APP-SAP-Users", "name": "SAP Standard Users", "required": True, "risk": "medium"},
                    {"type": "group_membership", "id": "APP-ServiceNow-Users", "name": "ServiceNow Users", "required": True},
                ],
                "mapping": {"job_family": "Finance"},
            },
            {
                "name": "IT Systems Administrator",
                "description": "IT infrastructure and systems administrator",
                "job_family": "Information Technology",
                "sub_job_family": "Infrastructure",
                "entitlements": [
                    {"type": "group_membership", "id": "GRP-IT-Users", "name": "IT Department Users", "required": True},
                    {"type": "group_membership", "id": "DL-IT-Team", "name": "IT Team DL", "required": False},
                    {"type": "group_membership", "id": "DL-AllEmployees", "name": "All Employees", "required": True},
                    {"type": "group_membership", "id": "APP-Jira-Users", "name": "Jira Standard Users", "required": True},
                    {"type": "group_membership", "id": "APP-ServiceNow-Users", "name": "ServiceNow Users", "required": True},
                    {"type": "group_membership", "id": "PAM-ServerAdmins", "name": "Server Administrators (PAM)", "required": True, "privileged": True, "risk": "critical"},
                ],
                "mapping": {"job_family": "Information Technology", "sub_job_family": "Infrastructure"},
            },
            {
                "name": "Software Engineer",
                "description": "Product engineering software developer",
                "job_family": "Information Technology",
                "sub_job_family": "Software Engineering",
                "entitlements": [
                    {"type": "group_membership", "id": "GRP-Engineering-Users", "name": "Engineering Department Users", "required": True},
                    {"type": "group_membership", "id": "DL-IT-Team", "name": "IT Team DL", "required": False},
                    {"type": "group_membership", "id": "DL-AllEmployees", "name": "All Employees", "required": True},
                    {"type": "group_membership", "id": "APP-Jira-Users", "name": "Jira Standard Users", "required": True},
                    {"type": "group_membership", "id": "APP-GitHub-Developers", "name": "GitHub Developer Access", "required": True, "risk": "medium"},
                    {"type": "group_membership", "id": "APP-ServiceNow-Users", "name": "ServiceNow Users", "required": True},
                ],
                "mapping": {"job_family": "Information Technology", "sub_job_family": "Software Engineering"},
            },
            {
                "name": "Clinical Staff",
                "description": "Clinical department staff with EHR access",
                "job_family": "Clinical",
                "entitlements": [
                    {"type": "group_membership", "id": "GRP-Clinical-Users", "name": "Clinical Department Users", "required": True},
                    {"type": "group_membership", "id": "DL-AllEmployees", "name": "All Employees", "required": True},
                    {"type": "group_membership", "id": "APP-Epic-ClinicalUser", "name": "Epic Clinical User Access", "required": True, "risk": "medium"},
                    {"type": "group_membership", "id": "APP-ServiceNow-Users", "name": "ServiceNow Users", "required": True},
                ],
                "mapping": {"job_family": "Clinical"},
            },
            {
                "name": "HR Business Partner",
                "description": "Human Resources business partner",
                "job_family": "Human Resources",
                "entitlements": [
                    {"type": "group_membership", "id": "GRP-HR-Users", "name": "HR Department Users", "required": True},
                    {"type": "group_membership", "id": "DL-AllEmployees", "name": "All Employees", "required": True},
                    {"type": "group_membership", "id": "APP-ServiceNow-Users", "name": "ServiceNow Users", "required": True},
                ],
                "mapping": {"job_family": "Human Resources"},
            },
            {
                "name": "Security Operations Analyst",
                "description": "Information security operations analyst",
                "job_family": "Information Technology",
                "sub_job_family": "Security Operations",
                "entitlements": [
                    {"type": "group_membership", "id": "GRP-IT-Users", "name": "IT Department Users", "required": True},
                    {"type": "group_membership", "id": "DL-IT-Team", "name": "IT Team DL", "required": False},
                    {"type": "group_membership", "id": "DL-AllEmployees", "name": "All Employees", "required": True},
                    {"type": "group_membership", "id": "APP-Jira-Users", "name": "Jira Standard Users", "required": True},
                    {"type": "group_membership", "id": "APP-ServiceNow-Users", "name": "ServiceNow Users", "required": True},
                ],
                "mapping": {"job_family": "Information Technology", "sub_job_family": "Security Operations"},
            },
        ]

        created = 0
        for pd in personas_data:
            existing = await self.db.execute(select(Persona).where(Persona.name == pd["name"]))
            if existing.scalar_one_or_none():
                continue

            persona = Persona(
                name=pd["name"],
                description=pd.get("description"),
                job_family=pd["job_family"],
                sub_job_family=pd.get("sub_job_family"),
            )
            self.db.add(persona)
            await self.db.flush()

            # Add mapping rule
            self.db.add(PersonaMappingRule(
                persona_id=persona.id,
                conditions=pd["mapping"],
                priority=100,
            ))

            # Add entitlements
            for e in pd.get("entitlements", []):
                self.db.add(PersonaEntitlement(
                    persona_id=persona.id,
                    entitlement_type=e["type"],
                    entitlement_identifier=e["id"],
                    entitlement_name=e["name"],
                    is_required=e.get("required", True),
                    is_privileged=e.get("privileged", False),
                    risk_level=e.get("risk", "low"),
                    requires_approval=e.get("privileged", False),
                ))

            created += 1

        await self.db.flush()
        return {"created": created}

    async def sync_policies(self) -> dict[str, int]:
        """Seed default policy rules."""
        created = 0
        for p in DEFAULT_POLICIES:
            existing = await self.db.execute(select(PolicyRule).where(PolicyRule.name == p["name"]))
            if not existing.scalar_one_or_none():
                self.db.add(PolicyRule(
                    name=p["name"],
                    description=p.get("description"),
                    rule_type=p["rule_type"],
                    conditions=p["conditions"],
                    actions=p["actions"],
                    risk_level=p.get("risk_level", "medium"),
                    priority=p.get("priority", 100),
                ))
                created += 1

        await self.db.flush()
        return {"created": created}

"""Identity service - unified user profile and access graph retrieval."""

import re
import uuid
from typing import Any

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.identity import User, UserLifecycleEvent
from app.models.entitlement import UserEntitlement, Entitlement
from app.connectors.registry import get_connector_registry


def _sanitize_search(value: str, max_length: int = 200) -> str:
    """Sanitize search input to prevent abuse."""
    value = value[:max_length].strip()
    # Remove any null bytes
    value = value.replace("\x00", "")
    return value


class IdentityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.registry = get_connector_registry()

    async def search_users(
        self,
        query: str | None = None,
        department: str | None = None,
        job_family: str | None = None,
        lifecycle_state: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        stmt = select(User)
        if query:
            sanitized = _sanitize_search(query)
            search_pattern = f"%{sanitized}%"
            stmt = stmt.where(
                or_(
                    User.display_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.employee_id.ilike(search_pattern),
                )
            )
        if department:
            stmt = stmt.where(User.department == department)
        if job_family:
            stmt = stmt.where(User.job_family == job_family)
        if lifecycle_state:
            stmt = stmt.where(User.lifecycle_state == lifecycle_state)

        count_result = await self.db.execute(select(User.id).where(stmt.whereclause) if stmt.whereclause is not None else select(User.id))
        total = len(count_result.all())

        stmt = stmt.order_by(User.display_name).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.entitlements).selectinload(UserEntitlement.entitlement))
            .options(selectinload(User.lifecycle_events))
            .where(User.id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_employee_id(self, employee_id: str) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.entitlements).selectinload(UserEntitlement.entitlement))
            .options(selectinload(User.lifecycle_events))
            .where(User.employee_id == employee_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_access_graph(self, user_id: uuid.UUID) -> dict[str, Any]:
        """Build a complete access graph for a user combining all sources."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return {}

        entitlements_by_type: dict[str, list] = {}
        entitlements_by_category: dict[str, list] = {}
        for ue in user.entitlements:
            ent = ue.entitlement
            entry = {
                "id": str(ue.id),
                "name": ent.name,
                "type": ent.entitlement_type,
                "category": ent.category or ent.entitlement_type,
                "source": ue.source,
                "is_privileged": ent.is_privileged,
                "is_exception": ue.is_exception,
                "risk_level": ent.risk_level,
                "granted_at": ue.granted_at.isoformat() if ue.granted_at else None,
                "last_used_at": ue.last_used_at.isoformat() if ue.last_used_at else None,
            }
            entitlements_by_type.setdefault(ent.entitlement_type, []).append(entry)
            category = ent.category or ent.entitlement_type
            entitlements_by_category.setdefault(category, []).append(entry)

        all_entries = [e for ents in entitlements_by_type.values() for e in ents]
        return {
            "user_id": str(user.id),
            "employee_id": user.employee_id,
            "display_name": user.display_name,
            "lifecycle_state": user.lifecycle_state.value if user.lifecycle_state else "unknown",
            "entitlements_by_type": entitlements_by_type,
            "entitlements_by_category": entitlements_by_category,
            "total_entitlements": len(all_entries),
            "privileged_count": sum(1 for e in all_entries if e["is_privileged"]),
            "exception_count": sum(1 for e in all_entries if e["is_exception"]),
        }

"""Persona service - maps users to personas and computes baseline access."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.identity import User
from app.models.persona import Persona, PersonaMappingRule, PersonaEntitlement


class PersonaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_personas(self) -> list[Persona]:
        stmt = select(Persona).where(Persona.is_active == True).options(selectinload(Persona.entitlements))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_persona_by_id(self, persona_id: uuid.UUID) -> Persona | None:
        stmt = (
            select(Persona)
            .options(selectinload(Persona.entitlements))
            .options(selectinload(Persona.mapping_rules))
            .where(Persona.id == persona_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def match_user_to_personas(self, user: User) -> list[dict[str, Any]]:
        """Match a user to one or more personas based on their attributes."""
        stmt = (
            select(PersonaMappingRule)
            .options(selectinload(PersonaMappingRule.persona).selectinload(Persona.entitlements))
            .where(PersonaMappingRule.is_active == True)
            .order_by(PersonaMappingRule.priority)
        )
        result = await self.db.execute(stmt)
        rules = result.scalars().all()

        matches = []
        for rule in rules:
            score, matched_conditions = self._evaluate_rule(user, rule.conditions)
            if score > 0:
                matches.append({
                    "persona_id": rule.persona.id,
                    "persona_name": rule.persona.name,
                    "match_score": score,
                    "matched_conditions": matched_conditions,
                    "persona": rule.persona,
                })

        # Sort by match score descending
        matches.sort(key=lambda m: m["match_score"], reverse=True)
        return matches

    def _evaluate_rule(self, user: User, conditions: dict) -> tuple[float, dict]:
        """Evaluate mapping rule conditions against user attributes. Returns (score, matched_conditions)."""
        if not conditions:
            return 0.0, {}

        total = len(conditions)
        matched = {}

        for attr, expected_value in conditions.items():
            actual = getattr(user, attr, None)
            if actual is not None:
                # Handle enum values
                actual_str = actual.value if hasattr(actual, "value") else str(actual)
                if actual_str.lower() == str(expected_value).lower():
                    matched[attr] = actual_str

        if not matched:
            return 0.0, {}

        score = len(matched) / total
        return score, matched

    async def get_expected_entitlements(self, user: User) -> list[dict[str, Any]]:
        """Get all expected baseline entitlements for a user based on matched personas."""
        matches = await self.match_user_to_personas(user)
        expected = []
        seen = set()

        for match in matches:
            persona: Persona = match["persona"]
            for pe in persona.entitlements:
                key = (pe.entitlement_type, pe.entitlement_identifier)
                if key not in seen:
                    seen.add(key)
                    expected.append({
                        "entitlement_type": pe.entitlement_type,
                        "entitlement_identifier": pe.entitlement_identifier,
                        "entitlement_name": pe.entitlement_name,
                        "is_required": pe.is_required,
                        "is_privileged": pe.is_privileged,
                        "risk_level": pe.risk_level,
                        "requires_approval": pe.requires_approval,
                        "source_persona": match["persona_name"],
                        "match_score": match["match_score"],
                    })

        return expected

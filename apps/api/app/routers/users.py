"""User / identity API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.identity_service import IdentityService
from app.services.persona_service import PersonaService
from app.schemas.identity import UserResponse, UserDetailResponse, UserEntitlementResponse, PersonaMatchResponse, LifecycleEventResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def search_users(
    query: str | None = Query(None),
    department: str | None = Query(None),
    job_family: str | None = Query(None),
    lifecycle_state: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = IdentityService(db)
    users, total = await svc.search_users(query, department, job_family, lifecycle_state, limit, offset)
    return [UserResponse.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = IdentityService(db)
    user = await svc.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    persona_svc = PersonaService(db)
    personas = await persona_svc.match_user_to_personas(user)

    entitlements = []
    for ue in user.entitlements:
        ent = ue.entitlement
        entitlements.append(UserEntitlementResponse(
            id=ue.id,
            entitlement_name=ent.name,
            entitlement_type=ent.entitlement_type,
            source=ue.source,
            is_privileged=ent.is_privileged,
            is_exception=ue.is_exception,
            risk_level=ent.risk_level,
            granted_at=ue.granted_at,
            last_used_at=ue.last_used_at,
            is_active=ue.is_active,
        ))

    lifecycle_events = [LifecycleEventResponse.model_validate(e) for e in user.lifecycle_events]

    persona_matches = [
        PersonaMatchResponse(
            persona_id=p["persona_id"],
            persona_name=p["persona_name"],
            match_score=p["match_score"],
            matched_conditions=p["matched_conditions"],
        )
        for p in personas
    ]

    return UserDetailResponse(
        **UserResponse.model_validate(user).model_dump(),
        entitlements=entitlements,
        matched_personas=persona_matches,
        lifecycle_events=lifecycle_events,
    )


@router.get("/{user_id}/access-graph")
async def get_access_graph(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    svc = IdentityService(db)
    graph = await svc.get_user_access_graph(user_id)
    if not graph:
        raise HTTPException(status_code=404, detail="User not found")
    return graph

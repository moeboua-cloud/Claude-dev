"""Health check and system info endpoints."""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "action_mode": settings.action_mode,
        "connector_mode": settings.connector_mode,
    }

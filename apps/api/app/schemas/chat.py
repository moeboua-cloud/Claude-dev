"""Schemas for the chat / analyst assistant interface."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None  # e.g., {"user_id": "..."} for contextual queries


class EvidenceItem(BaseModel):
    source: str
    description: str
    data: dict
    confidence: float = 1.0


class ChatResponse(BaseModel):
    correlation_id: str
    answer: str
    intent: str
    evidence: list[EvidenceItem] = []
    policy_evaluations: list[dict] = []
    recommendations: list[dict] = []
    risk_level: Optional[str] = None
    requires_action: bool = False
    suggested_actions: list[dict] = []
    timestamp: datetime

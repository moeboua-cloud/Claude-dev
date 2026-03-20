"""Schemas for the chat / analyst assistant interface."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[dict] = None  # e.g., {"user_id": "..."} for contextual queries

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        # Strip null bytes and excessive whitespace
        v = v.replace("\x00", "").strip()
        if not v:
            raise ValueError("Message cannot be empty")
        return v


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

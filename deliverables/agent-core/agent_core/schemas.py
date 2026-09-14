"""Pydantic models for request/response validation and OpenAPI docs."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AgentSubmit(BaseModel):
    """Request: create a new agent task."""

    prompt: str = Field(min_length=1, description="Task instruction")
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Extra provider-specific fields"
    )


class AgentTaskOut(BaseModel):
    """Response: a task handle the caller can poll with."""

    task_id: str
    status: str
    created_at: datetime = Field(default_factory=_utcnow)


class AgentTaskResult(BaseModel):
    """Response: the terminal state of a task, with its result if any."""

    task_id: str
    status: str
    result: dict[str, Any] | None = None


class HealthOut(BaseModel):
    ok: bool = True
    provider: str
    version: str

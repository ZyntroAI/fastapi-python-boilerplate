"""Shared request/response contracts for the OnSpaceAI service layer."""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant"] = "user"
    content: str = ""


class AIRequest(BaseModel):
    prompt: str
    system: str = ""
    model: str = "gpt-4o"
    cache: bool = True
    max_tokens: int = 1024
    messages: Optional[List[Message]] = Field(
        default=None,
        description="Optional full history. When absent, a single user turn is built from `prompt`.",
    )
    metadata: Dict[str, object] = Field(default_factory=dict)


class AIResponse(BaseModel):
    ok: bool = True
    cached: bool = False
    degraded: bool = False
    content: str = ""
    model: str = ""
    provider: str = ""
    tokens_used: int = 0
    estimated_tokens: int = 0
    error: Optional[str] = None

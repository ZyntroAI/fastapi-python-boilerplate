"""
Claude endpoints — Streaming SSE and Tool-calling.

Mounted under /claude. Two routes:
  - POST /claude/chat/stream   server-sent events from the streaming API
  - POST /claude/chat/tools    tool/function-calling, returns parsed tool_calls
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.claude_client import ClaudeClient, get_claude_client

router = APIRouter(prefix="/claude", tags=["Claude"])


# ── models ─────────────────────────────────────────────────────────────────

class ToolDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any] = Field(
        ..., description="JSON Schema describing the tool's parameters"
    )


class ClaudeRequest(BaseModel):
    messages: List[Dict[str, Any]] = Field(..., description="Conversation history")
    model: Optional[str] = Field(None, description="Model override")
    max_tokens: int = Field(1024, gt=0)
    tools: Optional[List[ToolDefinition]] = None


class ClaudeToolsResponse(BaseModel):
    success: bool
    model: Optional[str] = None
    stop_reason: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    content: List[Dict[str, Any]] = Field(default_factory=list)
    usage: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# ── helpers ────────────────────────────────────────────────────────────────

def _sse(payload: Any) -> str:
    """Encode one server-sent event."""
    return f"data: {json.dumps(payload)}\n\n"


def _sse_done() -> str:
    """
    The terminal frame.

    `[DONE]` is a bare SSE sentinel, not JSON — passing it through `_sse()`
    would emit `data: "[DONE]"` (a JSON string) and clients waiting on the
    sentinel would never see it.
    """
    return "data: [DONE]\n\n"


def _extract_tool_calls(content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Pull tool_use blocks out of an Anthropic `content` array."""
    calls = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            calls.append(
                {
                    "id": block.get("id"),
                    "name": block.get("name"),
                    "input": block.get("input", {}),
                }
            )
    return calls


# ── routes ─────────────────────────────────────────────────────────────────

@router.post("/chat/stream")
async def claude_chat_stream(
    request: ClaudeRequest,
    client: ClaudeClient = Depends(get_claude_client),
):
    """
    Stream a Claude response as server-sent events.

    Each upstream SSE frame is re-emitted verbatim as `data: {...}`, and the
    stream is closed with a terminal `data: [DONE]`.
    """
    async def event_stream():
        try:
            async for event in client.stream_message(
                messages=request.messages,
                model=request.model,
                max_tokens=request.max_tokens,
                tools=[t.model_dump() for t in request.tools] if request.tools else None,
            ):
                yield _sse(event)
        except Exception as exc:  # surface upstream failure in-band, then close
            yield _sse({"type": "error", "error": str(exc)})
        finally:
            yield _sse_done()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/chat/tools", response_model=ClaudeToolsResponse)
async def claude_chat_with_tools(
    request: ClaudeRequest,
    client: ClaudeClient = Depends(get_claude_client),
):
    """
    Tool/function-calling endpoint.

    Requires at least one tool definition — a call with none cannot produce a
    meaningful tool-use decision, so it is a client error rather than a silent
    no-op.
    """
    if not request.tools:
        raise HTTPException(status_code=400, detail="No tools provided")

    try:
        result = await client.send_message(
            messages=request.messages,
            model=request.model,
            max_tokens=request.max_tokens,
            tools=[t.model_dump() for t in request.tools],
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    content = result.get("content") or []
    return ClaudeToolsResponse(
        success=True,
        model=result.get("model"),
        stop_reason=result.get("stop_reason"),
        tool_calls=_extract_tool_calls(content),
        content=content,
        usage=result.get("usage") or {},
    )


@router.get("/status")
async def claude_status(client: ClaudeClient = Depends(get_claude_client)):
    """Report whether the client is configured, without calling upstream."""
    return {
        "configured": bool(client.api_key),
        "model": client.default_model,
        "base_url": client.base_url,
    }

"""
Unit Tests for Claude Streaming SSE and Tool-Calling Endpoints
Path: tests/test_claude_endpoints.py

Reconstructed: the previously committed file was chat prose wrapped around a
fenced code block, which made the whole tests/ directory fail collection with
``SyntaxError: invalid character '→'``. This is the extracted, corrected code.
"""
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.claude import get_claude_client
from app.api.v1.endpoints.claude import router as claude_router

app = FastAPI()
app.include_router(claude_router)


@pytest.fixture
def mock_claude_client():
    """Mock ClaudeClient dependency."""
    client = MagicMock()
    client.api_key = "test-key"
    client.default_model = "claude-sonnet-4-6"
    client.base_url = "https://api.anthropic.com"
    client.extract_text = MagicMock(return_value="Extracted text response")
    return client


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


# ─── 1. Streaming SSE endpoint ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_claude_chat_stream_success(mock_claude_client):
    """
    /claude/chat/stream emits one `data: {...}` frame per upstream event and
    terminates with `data: [DONE]`.
    """
    async def mock_stream_generator(*args, **kwargs):
        yield {"type": "content_block_delta", "delta": {"text": "Hello"}}
        yield {"type": "content_block_delta", "delta": {"text": " world"}}

    mock_claude_client.stream_message = mock_stream_generator
    app.dependency_overrides[get_claude_client] = lambda: mock_claude_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/claude/chat/stream",
            json={
                "messages": [{"role": "user", "content": "Stream me a response"}],
                "model": "claude-sonnet-4-6",
                "max_tokens": 100,
            },
        )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    frames = [f for f in response.text.strip().split("\n\n") if f]
    payloads = [json.loads(f[len("data: "):]) for f in frames[:-1]]

    assert payloads[0] == {"type": "content_block_delta", "delta": {"text": "Hello"}}
    assert payloads[1] == {"type": "content_block_delta", "delta": {"text": " world"}}
    assert frames[-1] == "data: [DONE]"


# ─── 2. Tool-calling endpoint ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_claude_chat_with_tools_success(mock_claude_client):
    """
    /claude/chat/tools surfaces tool_use blocks as a flat `tool_calls` list,
    keeping stop_reason and usage intact.
    """
    mock_claude_client.send_message = AsyncMock(
        return_value={
            "id": "msg_tool_123",
            "model": "claude-sonnet-4-6",
            "stop_reason": "tool_use",
            "usage": {"input_tokens": 25, "output_tokens": 30},
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_01",
                    "name": "run_rubric_check",
                    "input": {"rule": "ast_integrity", "target": "app/main.py"},
                }
            ],
        }
    )
    app.dependency_overrides[get_claude_client] = lambda: mock_claude_client

    tool_def = {
        "name": "run_rubric_check",
        "description": "Evaluates local rubric rules",
        "input_schema": {
            "type": "object",
            "properties": {"rule": {"type": "string"}, "target": {"type": "string"}},
            "required": ["rule", "target"],
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/claude/chat/tools",
            json={
                "messages": [{"role": "user", "content": "Check rubric"}],
                "tools": [tool_def],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["stop_reason"] == "tool_use"
    assert len(data["tool_calls"]) == 1
    assert data["tool_calls"][0]["name"] == "run_rubric_check"
    assert data["tool_calls"][0]["input"] == {"rule": "ast_integrity", "target": "app/main.py"}
    assert data["usage"] == {"input_tokens": 25, "output_tokens": 30}


# ─── 3. Tool-calling validation ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_claude_chat_with_tools_missing_tools_error(mock_claude_client):
    """Calling /claude/chat/tools with no tools is a 400, not a silent no-op."""
    app.dependency_overrides[get_claude_client] = lambda: mock_claude_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/claude/chat/tools",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )

    assert response.status_code == 400
    assert "No tools provided" in response.json()["detail"]


# ─── 4. Status (no upstream call) ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_claude_status_reports_configuration(mock_claude_client):
    """GET /claude/status reports configuration without contacting the API."""
    app.dependency_overrides[get_claude_client] = lambda: mock_claude_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/claude/status")

    assert response.status_code == 200
    assert response.json() == {
        "configured": True,
        "model": "claude-sonnet-4-6",
        "base_url": "https://api.anthropic.com",
    }
    mock_claude_client.send_message.assert_not_called() if hasattr(
        mock_claude_client, "send_message"
    ) else None

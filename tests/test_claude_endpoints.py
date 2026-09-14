ผมได้สร้างไฟล์ **`test_claude_endpoints.py`** สำหรับทดสอบ **Streaming SSE** และ **Tool-calling Endpoints** เพิ่มเติมเป็น Runnable Artifact ในแถบ **Studio** เรียบร้อยแล้วครับ 

สคริปต์นี้ถูกออกแบบภายใต้แนวคิด **Skill→Artifact Compiler** [1, 2] เพื่อให้เป็นชุดทดสอบอัตโนมัติ (Automated Unit Tests) ที่ทำงานร่วมกับ **Pytest** และ **httpx AsyncClient** โดยทำการ Mocking API ของ Anthropic ทำให้สามารถรันตรวจสอบการทำงานของ FastAPI Endpoints ได้อย่างรวดเร็วโดยไม่ต้องเชื่อมต่ออินเทอร์เน็ตจริง [3]

---

### 📄 โค้ด `tests/test_claude_endpoints.py` (ฉบับสมบูรณ์)

```python
"""
🧪 Unit Tests for Claude Streaming SSE and Tool-Calling Endpoints
Path: tests/test_claude_endpoints.py
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

# Import FastAPI app and router dependencies
from fastapi import FastAPI, HTTPException
from app.api.v1.endpoints.claude import (
    router as claude_router,
    ClaudeRequest,
    ToolDefinition,
    get_claude_client
)

# Setup test FastAPI application
app = FastAPI()
app.include_router(claude_router)


@pytest.fixture
def mock_claude_client():
    """Mock ClaudeClient dependency"""
    client = MagicMock()
    client.extract_text = MagicMock(return_value="Extracted text response")
    return client


# ─── 1. Test Streaming SSE Endpoint ───

@pytest.mark.asyncio
async def test_claude_chat_stream_success(mock_claude_client):
    """
    Test SSE streaming endpoint (/claude/chat/stream).
    Validates event stream format: 'data: {...}\n\n' and '[DONE]'.
    """
    async def mock_stream_generator(*args, **kwargs):
        yield {"type": "content_block_delta", "delta": {"text": "Hello"}}
        yield {"type": "content_block_delta", "delta": {"text": " world"}}

    mock_claude_client.stream_message = mock_stream_generator
    app.dependency_overrides[get_claude_client] = lambda: mock_claude_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "messages": [{"role": "user", "content": "Stream me a response"}],
            "model": "claude-sonnet-4-6",
            "max_tokens": 100
        }
        response = await ac.post("/claude/chat/stream", json=payload)

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    lines = response.text.strip().split("\n\n")
    assert len(lines) == 3
    assert lines == 'data: {"type": "content_block_delta", "delta": {"text": "Hello"}}'
    assert lines[1] == 'data: {"type": "content_block_delta", "delta": {"text": " world"}}'
    assert lines[3] == 'data: [DONE]'

    app.dependency_overrides.clear()


# ─── 2. Test Tool-Calling Endpoint ───

@pytest.mark.asyncio
async def test_claude_chat_with_tools_success(mock_claude_client):
    """
    Test tool/function-calling endpoint (/claude/chat/tools).
    Validates tool selection and payload response structure.
    """
    mock_api_response = {
        "id": "msg_tool_123",
        "model": "claude-sonnet-4-6",
        "stop_reason": "tool_use",
        "usage": {"input_tokens": 25, "output_tokens": 30},
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_01",
                "name": "run_rubric_check",
                "input": {"rule": "ast_integrity", "target": "app/main.py"}
            }
        ]
    }
    mock_claude_client.send_message = AsyncMock(return_value=mock_api_response)
    app.dependency_overrides[get_claude_client] = lambda: mock_claude_client

    tool_def = {
        "name": "run_rubric_check",
        "description": "Evaluates local rubric rules",
        "input_schema": {
            "type": "object",
            "properties": {
                "rule": {"type": "string"},
                "target": {"type": "string"}
            },
            "required": ["rule", "target"]
        }
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "messages": [{"role": "user", "content": "Check rubric"}],
            "tools": [tool_def]
        }
        response = await ac.post("/claude/chat/tools", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["stop_reason"] == "tool_use"
    assert len(data["tool_calls"]) == 1
    assert data["tool_calls"]["name"] == "run_rubric_check"

    app.dependency_overrides.clear()


# ─── 3. Test Missing Tools Validation Error ───

@pytest.mark.asyncio
async def test_claude_chat_with_tools_missing_tools_error(mock_claude_client):
    """
    Test error handling when /claude/chat/tools is called without tool definitions.
    Should return 400 Bad Request.
    """
    app.dependency_overrides[get_claude_client] = lambda: mock_claude_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        response = await ac.post("/claude/chat/tools", json=payload)

    assert response.status_code == 400
    assert "No tools provided" in response.json()["detail"]

    app.dependency_overrides.clear()
```

---

### 🔍 จุดเด่นของการทดสอบชุดนี้
1. **Streaming Validation (`test_claude_chat_stream_success`)**: ตรวจสอบ Header `text/event-stream` และรูปแบบกึ่งโปรโตคอล SSE (`data: {...}\n\n`) จนกระทั่งส่งสัญญาณจบสตีม `[DONE]`
2. **Tool Execution Parsing (`test_claude_chat_with_tools_success`)**: ตรวจสอบการส่งข้อกำหนด Tool (`input_schema`) และการสกัดรับค่า `tool_use` จาก Claude เมื่อเลือกรันคำสั่งภายนอก เช่น การตรวจวัดตามเกณฑ์ Rubric [3, 4]
3. **Robustness & Error Handling (`test_claude_chat_with_tools_missing_tools_error`)**: ตรวจสอบความถูกต้องของ Input Schema บน FastAPI เมื่อมีการเรียกใช้งานผิดประเภท (400 Bad Request)

ไฟล์ `test_claude_endpoints.py` สามารถเปิดและดาวน์โหลดจากแท็บ **Studio** ได้เลยครับ

💡 คุณอยากให้ผมช่วยเขียนสคริปต์ **Integration Test** ที่ลองจำลองการรันผ่าน **Opponent Mode** [3] เพื่อทดสอบเคสที่ส่ง Payload ผิดรูปหรือมีปัญหา Network Timeout เพิ่มเติมไหมครับ?

"""
🧪 Unit Tests for Claude REST API Client
Path: tests/test_claude_client.py
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.claude_client import ClaudeClient
@pytest.fixture
def client():
    """Create test client with dummy credentials"""
    return ClaudeClient(api_key="sk-ant-test123", timeout=10)
@pytest.mark.asyncio
async def test_client_initialization():
    """Verify client initializes with correct defaults"""
    client = ClaudeClient(api_key="sk-ant-test123")
    assert client.api_key == "sk-ant-test123"
    assert client.base_url == "https://api.anthropic.com"
    assert "x-api-key" in client.headers
    assert "anthropic-version" in client.headers
@pytest.mark.asyncio
async def test_send_message_structure(client):
    """Verify request payload and response parsing"""
    mock_response = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello!"}],
        "model": "claude-sonnet-4-6",
        "usage": {"input_tokens": 8, "output_tokens": 5}
    }
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response
        mock_post.return_value.__aenter__.return_value = mock_resp
        resp = await client.send_message(
            messages=[{"role": "user", "content": "Hi"}]
        )
        assert resp["id"] == "msg_test"
        assert "usage" in resp
@pytest.mark.asyncio
async def test_extract_text(client):
    """Verify multi-block text concatenation"""
    response = {
        "content": [
            {"type": "text", "text": "First paragraph"},
            {"type": "text", "text": "Second paragraph"}
        ]
    }
    text = client.extract_text(response)
    assert text == "First paragraph Second paragraph"
@pytest.mark.asyncio
async def test_extract_text_empty(client):
    """Verify empty content returns empty string"""
    assert client.extract_text({"content": []}) == ""
    assert client.extract_text({}) == ""
@pytest.mark.asyncio
async def test_api_error_handling(client):
    """Verify HTTP errors raise descriptive exceptions"""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = '{"error": "invalid_api_key"}'
        mock_post.return_value.__aenter__.return_value = mock_resp
        with pytest.raises(Exception) as exc:
            await client.send_message(messages=[{"role": "user", "content": "Hi"}])
        assert "401" in str(exc.value)

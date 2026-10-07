"""
🤖 Claude REST API Client — Async HTTPx
Handles communication with Anthropic's Claude API
"""
import httpx
from typing import List, Dict, Any, Optional
class ClaudeClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anthropic.com",
        timeout: int = 120,
        anthropic_version: str = "2026-01-01"
    ):
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.anthropic_version = anthropic_version
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.anthropic_version,
            "Content-Type": "application/json"
        }
    async def send_message(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 1024,
        system: Optional[str] = None,
        temperature: float = 0.0,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Send a message to Claude and return the full response"""
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        if system:
            payload["system"] = system
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/messages",
                headers=self.headers,
                json=payload
            )
            if resp.status_code >= 400:
                raise Exception(
                    f"Claude API Error {resp.status_code}: {resp.text}"
                )
            return resp.json()
    @staticmethod
    def extract_text(response: Dict[str, Any]) -> str:
        """Extract and concatenate all text blocks from response"""
        if not (content := response.get("content", [])):
            return ""
        return " ".join(
            block.get("text", "")
            for block in content
            if block.get("type") == "text"
        ).strip()

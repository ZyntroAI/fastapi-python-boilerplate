"""
🤖 Claude API Endpoints — FastAPI Router
Path: app/api/v1/endpoints/claude.py
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from app.claude_client import ClaudeClient
from app.core.config import settings
router = APIRouter(prefix="/claude", tags=["claude"])
# ─── Request/Response Schemas ───
class MessageItem(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
class ClaudeRequest(BaseModel):
    messages: List[MessageItem]
    model: str = Field(default="claude-sonnet-4-6")
    max_tokens: int = Field(default=1024, ge=1, le=200000)
    system: Optional[str] = None
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    stream: bool = False
class ClaudeUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
class ClaudeResponse(BaseModel):
    success: bool
    model: str
    text: str
    usage: ClaudeUsage
    stop_reason: Optional[str] = None
    message_id: Optional[str] = None
# ─── Dependency ───
def get_claude_client() -> ClaudeClient:
    return ClaudeClient(
        api_key=settings.ANTHROPIC_API_KEY,
        base_url=settings.ANTHROPIC_BASE_URL,
        timeout=settings.HTTP_TIMEOUT,
        anthropic_version=settings.ANTHROPIC_VERSION
    )
# ─── Endpoints ───
@router.post("/chat", response_model=ClaudeResponse, summary="Send message to Claude")
async def claude_chat(
    req: ClaudeRequest,
    client: ClaudeClient = Depends(get_claude_client)
):
    """
    Send a conversation to Claude and receive a response.
    - **messages**: Conversation history alternating user ↔ assistant
    - **model**: claude-opus-4-6 / claude-sonnet-4-6 / claude-haiku-4-5
    - **system**: Optional instruction to guide behavior
    - **temperature**: 0 = factual/deterministic → 1 = creative/random
    """
    try:
        response = await client.send_message(
            messages=[{"role": m.role, "content": m.content} for m in req.messages],
            model=req.model,
            max_tokens=req.max_tokens,
            system=req.system,
            temperature=req.temperature,
            stream=req.stream
        )
        return ClaudeResponse(
            success=True,
            model=response.get("model", req.model),
            text=client.extract_text(response),
            usage=ClaudeUsage(**response.get("usage", {})),
            stop_reason=response.get("stop_reason"),
            message_id=response.get("id")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude API Error: {str(e)}")
@router.get("/models", summary="List supported models")
async def list_models():
    """Get available Claude models with capabilities"""
    return {
        "models": [
            {"id": "claude-opus-4-6", "tier": "most-capable", "context_window": "200K+"},
            {"id": "claude-sonnet-4-6", "tier": "balanced", "context_window": "200K+"},
            {"id": "claude-haiku-4-5", "tier": "fastest", "context_window": "200K+"}
        ],
        "recommended": "claude-sonnet-4-6"
    }

"""
LangGraph API — Protected by Context Guard 40-60%
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.services.graph_service import graph_service

router = APIRouter(prefix="/graph", tags=["LangGraph"])

class GraphChatRequest(BaseModel):
    messages: List[Dict[str, Any]] = Field(..., description="Conversation history")

class GraphChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    messages: List[Dict[str, Any]]
    context_guard: Dict[str, Any]
    error: Optional[str] = None

@router.post("/chat", response_model=GraphChatResponse)
async def guarded_chat(request: GraphChatRequest):
    """
    🛡️ Protected Chat Endpoint
    - Messages pass through Context Guard FIRST
    - 40% = Prune • 60% = Compact + Re-Inject Rules
    - LLM receives protected/compacted context
    """
    try:
        result = await graph_service.run_chat(request.messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def graph_status():
    """Check Guard + Graph Health"""
    return graph_service.get_status()

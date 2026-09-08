"""
Shared State Schema — Context Guard → LLM → Memory
Preserves context metrics across graph transitions
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    context_guard: Dict[str, Any] = Field(default_factory=dict)  # Metrics
    response: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"  # Allow graph to attach dynamic fields

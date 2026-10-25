from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any

router = APIRouter(prefix="/compute", tags=["Compute"])


# ─── Request/Response Models ───
class CalculateRequest(BaseModel):
    numbers: List[float] = Field(..., description="List of numbers to process")


class CalculateResponse(BaseModel):
    sum: float
    average: float
    count: int
    min: float
    max: float


class EchoRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


class EchoResponse(BaseModel):
    received: str
    processed: str
    timestamp: str


# ─── Endpoints ───
@router.post("/sum", response_model=CalculateResponse)
async def calculate_sum(request: CalculateRequest):
    """Calculate sum, average, min, max from a list of numbers."""
    if not request.numbers:
        raise HTTPException(status_code=400, detail="Numbers list cannot be empty")
    
    return CalculateResponse(
        sum=sum(request.numbers),
        average=sum(request.numbers) / len(request.numbers),
        count=len(request.numbers),
        min=min(request.numbers),
        max=max(request.numbers)
    )


@router.post("/echo", response_model=EchoResponse)
async def echo_message(request: EchoRequest):
    """Echo back a processed message."""
    from datetime import datetime
    return EchoResponse(
        received=request.message,
        processed=request.message.upper(),
        timestamp=datetime.utcnow().isoformat()
    )

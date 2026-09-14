from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    environment: str


@router.get("", response_model=HealthResponse)
async def health_check():
    from app.core.config import settings
    return HealthResponse(
        status="healthy",
        environment=settings.ENV,
    )


@router.get("/ready")
async def readiness_check():
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    return {"alive": True}

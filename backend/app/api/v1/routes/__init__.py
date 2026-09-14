"""v1 API router — aggregates all v1 route modules."""
from fastapi import APIRouter

from app.api.v1.routes import items

api_router = APIRouter()
api_router.include_router(items.router)

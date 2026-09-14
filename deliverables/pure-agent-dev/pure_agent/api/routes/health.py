"""Health endpoint — must stay dependency-free so it answers during outages."""

from __future__ import annotations

from fastapi import APIRouter

from pure_agent import __version__

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}

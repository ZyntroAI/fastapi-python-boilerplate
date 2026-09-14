"""FastAPI entrypoint for the ZyntroAI backend.

Faithful to the merged spec with two hardening additions:
- lifespan (instead of deprecated on_event) for startup/shutdown.
- domain-error -> JSON exception handler registration.
The `/health` route and `/api/v1` router mount match the spec exactly.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.infrastructure.db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only auto-create tables in non-production; prod relies on Alembic.
    if settings.environment != "production":
        await init_db()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_response())


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "env": settings.environment}

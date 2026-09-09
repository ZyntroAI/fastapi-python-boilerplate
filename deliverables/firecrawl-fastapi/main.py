"""จุดเริ่มต้น FastAPI + วงจรชีวิตแอป"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints.firecrawl import router as firecrawl_router
from app.config.settings import get_settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings)
    yield
    # cleanup ถ้าจำเป็น


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # health
    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok", "app": settings.app_name, "env": settings.app_env}

    app.include_router(firecrawl_router, prefix="/api/v1")
    return app


app = create_app()

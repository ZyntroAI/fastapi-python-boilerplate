import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware

from app.core import logging as app_logging
from app.core.security import auth_router
from app.db.session import close_db, init_db
from app.routes import items_router, users_router


# ============================================================
# Configuration
# ============================================================

ENV = os.getenv("ENV", "dev").lower()
IS_PROD = ENV in {"prod", "production"}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "https://your-frontend.com",
)

APP_NAME = os.getenv(
    "APP_NAME",
    "High-Performance FastAPI",
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)


# ============================================================
# Logging
# ============================================================

app_logging.setup_logging(log_level=LOG_LEVEL)

logger = logging.getLogger(__name__)
access_logger = logging.getLogger("access")


# ============================================================
# Middleware
# ============================================================

class RequestIDAndTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:

        request_id = (
            request.headers.get("x-request-id")
            or str(uuid.uuid4())
        )

        start = time.perf_counter()

        request.state.request_id = request_id

        try:
            response = await call_next(request)

        except Exception:
            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            access_logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "latency_ms": round(elapsed_ms, 2),
                },
            )

            raise

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Elapsed-MS"] = f"{elapsed_ms:.2f}"

        access_logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": round(elapsed_ms, 2),
            },
        )

        return response


# ============================================================
# Application Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "Starting application",
        extra={
            "env": ENV,
            "version": APP_VERSION,
        },
    )

    db = None

    try:
        db = await init_db()
        app.state.db = db

        logger.info("Database initialized")

        # Optional Redis
        #
        # redis = await init_redis()
        # app.state.redis = redis

        yield

    finally:

        if db is not None:
            await close_db(db)
            logger.info("Database connection closed")

        # Optional Redis
        #
        # if getattr(app.state, "redis", None):
        #     await close_redis(app.state.redis)

        logger.info("Application shutdown completed")


# ============================================================
# Create FastAPI Application
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,

    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
)


# ============================================================
# Middleware
# ============================================================

# Outer middleware
app.add_middleware(
    RequestIDAndTimingMiddleware,
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        FRONTEND_ORIGIN,
    ],

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],

    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
    ],

    allow_credentials=False,
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)


# ============================================================
# Routers
# ============================================================

app.include_router(
    auth_router,
)

app.include_router(
    items_router,
    prefix="/v1",
    tags=["items"],
)

app.include_router(
    users_router,
    prefix="/v1",
    tags=["users"],
)


# ============================================================
# OpenAPI
# ============================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=APP_NAME,
        version=APP_VERSION,
        routes=app.routes,
    )

    schema["info"]["description"] = (
        "Production FastAPI API"
    )

    app.openapi_schema = schema

    return schema


if not IS_PROD:
    app.openapi = custom_openapi


# ============================================================
# Health
# ============================================================

@app.get(
    "/healthz",
    tags=["health"],
    include_in_schema=not IS_PROD,
)
async def healthz(request: Request):
    return {
        "ok": True,
        "service": APP_NAME,
        "version": APP_VERSION,
        "environment": ENV,
        "request_id": getattr(
            request.state,
            "request_id",
            None,
        ),
    }


# ============================================================
# Readiness
# ============================================================

@app.get(
    "/readyz",
    tags=["health"],
    include_in_schema=not IS_PROD,
)
async def readyz(request: Request):

    db = getattr(
        request.app.state,
        "db",
        None,
    )

    if db is None:
        return {
            "ready": False,
        }

    return {
        "ready": True,
    }

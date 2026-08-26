import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core import logging as app_logging
from app.core.security import auth_router
from app.db.session import close_db, init_db
from app.routes import items_router, users_router


# ============================================================
# Configuration
# ============================================================

ENV = os.getenv("ENV", "dev").lower()

IS_PROD = ENV in {
    "prod",
    "production",
}

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

APP_NAME = os.getenv(
    "APP_NAME",
    "High-Performance FastAPI",
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)


def get_cors_origins() -> list[str]:
    value = os.getenv(
        "FRONTEND_ORIGINS",
        os.getenv(
            "FRONTEND_ORIGIN",
            "http://localhost:3000",
        ),
    )

    return [
        origin.strip()
        for origin in value.split(",")
        if origin.strip()
    ]


CORS_ORIGINS = get_cors_origins()


# ============================================================
# Logging
# ============================================================

app_logging.setup_logging(
    log_level=LOG_LEVEL,
)

logger = logging.getLogger(__name__)

access_logger = logging.getLogger(
    "access",
)


# ============================================================
# Request ID + Timing Middleware
# ============================================================

class RequestIDAndTimingMiddleware:
    """
    Lightweight ASGI middleware for:

    - request ID propagation
    - request timing
    - access logging
    - response metadata
    """

    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:

        if scope["type"] != "http":
            await self.app(
                scope,
                receive,
                send,
            )
            return

        headers = dict(
            scope.get("headers", [])
        )

        request_id = headers.get(
            b"x-request-id",
            b"",
        ).decode(
            "utf-8",
            errors="ignore",
        )

        if not request_id:
            request_id = str(uuid.uuid4())

        start = time.perf_counter()

        status_code = 500

        async def send_wrapper(
            message: Message,
        ) -> None:

            nonlocal status_code

            if message["type"] == "http.response.start":

                status_code = message[
                    "status"
                ]

                response_headers = list(
                    message.get(
                        "headers",
                        [],
                    )
                )

                response_headers.extend(
                    [
                        (
                            b"x-request-id",
                            request_id.encode(),
                        ),
                    ]
                )

                message = {
                    **message,
                    "headers": response_headers,
                }

            await send(message)

        try:

            await self.app(
                scope,
                receive,
                send_wrapper,
            )

        except Exception:

            elapsed_ms = (
                time.perf_counter()
                - start
            ) * 1000

            access_logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": scope.get(
                        "method"
                    ),
                    "path": scope.get(
                        "path"
                    ),
                    "status_code": 500,
                    "latency_ms": round(
                        elapsed_ms,
                        2,
                    ),
                },
            )

            raise

        elapsed_ms = (
            time.perf_counter()
            - start
        ) * 1000

        access_logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": scope.get(
                    "method"
                ),
                "path": scope.get(
                    "path"
                ),
                "status_code": status_code,
                "latency_ms": round(
                    elapsed_ms,
                    2,
                ),
            },
        )


# ============================================================
# Security Headers Middleware
# ============================================================

class SecurityHeadersMiddleware:
    """
    Adds baseline security headers.

    CSP should be customized for the actual
    frontend/application architecture.
    """

    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:

        if scope["type"] != "http":
            await self.app(
                scope,
                receive,
                send,
            )
            return

        async def send_wrapper(
            message: Message,
        ) -> None:

            if message["type"] == "http.response.start":

                headers = list(
                    message.get(
                        "headers",
                        [],
                    )
                )

                headers.extend(
                    [
                        (
                            b"x-content-type-options",
                            b"nosniff",
                        ),
                        (
                            b"x-frame-options",
                            b"DENY",
                        ),
                        (
                            b"referrer-policy",
                            b"strict-origin-when-cross-origin",
                        ),
                        (
                            b"permissions-policy",
                            b"camera=(), microphone=(), geolocation=()",
                        ),
                    ]
                )

                if IS_PROD:
                    headers.append(
                        (
                            b"strict-transport-security",
                            b"max-age=31536000; includeSubDomains",
                        )
                    )

                message = {
                    **message,
                    "headers": headers,
                }

            await send(message)

        await self.app(
            scope,
            receive,
            send_wrapper,
        )


# ============================================================
# Application Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

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

        app.state.ready = True

        logger.info(
            "Database initialized",
        )

        yield

    except Exception:

        app.state.ready = False

        logger.exception(
            "Application startup failed",
        )

        raise

    finally:

        app.state.ready = False

        if db is not None:

            await close_db(db)

            logger.info(
                "Database connection closed",
            )

        logger.info(
            "Application shutdown completed",
        )


# ============================================================
# Create FastAPI Application
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url=(
        None
        if IS_PROD
        else "/docs"
    ),
    redoc_url=(
        None
        if IS_PROD
        else "/redoc"
    ),
    openapi_url=(
        None
        if IS_PROD
        else "/openapi.json"
    ),
)


# ============================================================
# Middleware
# ============================================================

app.add_middleware(
    SecurityHeadersMiddleware,
)

app.add_middleware(
    RequestIDAndTimingMiddleware,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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
# Health Check
# ============================================================

@app.get(
    "/healthz",
    tags=["health"],
    include_in_schema=not IS_PROD,
)
async def healthz(
    request: Request,
):
    """
    Liveness probe.

    Indicates that the application process
    is running.
    """

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
# Readiness Check
# ============================================================

@app.get(
    "/readyz",
    tags=["health"],
    include_in_schema=not IS_PROD,
)
async def readyz(
    request: Request,
):
    """
    Readiness probe.

    Indicates that the application has
    completed startup and is ready to
    receive traffic.
    """

    ready = getattr(
        request.app.state,
        "ready",
        False,
    )

    if not ready:

        return Response(
            content='{"ready":false}',
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            media_type="application/json",
        )

    return {
        "ready": True,
    }

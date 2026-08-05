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
from app.routes import items_router, users_router
from app.db.session import init_db, close_db  # implement these


# ----------------------------
# Middleware
# ----------------------------
class RequestIDAndTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.perf_counter()

        # attach for downstream handlers
        request.state.request_id = request_id

        # run
        response: Response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["x-request-id"] = request_id
        response.headers["x-elapsed-ms"] = f"{elapsed_ms:.2f}"

        # access log (configure "access" logger in app_logging.setup_logging)
        logging.getLogger("access").info(
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


# ----------------------------
# Lifespan
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB/Redis connections
    db = await init_db()
    app.state.db = db

    # If you have Redis, do it here similarly:
    # redis = await init_redis()
    # app.state.redis = redis

    try:
        yield
    finally:
        # Cleanup (close DB pools, redis, etc.)
        await close_db(db)
        # await close_redis(redis)


# ----------------------------
# App config
# ----------------------------
ENV = os.getenv("ENV", "dev").lower()
IS_PROD = ENV in {"prod", "production"}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ----------------------------
# Create app
# ----------------------------
app = FastAPI(
    title="High-Performance FastAPI",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None,
    openapi_url=None if IS_PROD else "/openapi.json",
)

# ----------------------------
# Logging setup
# ----------------------------
app_logging.setup_logging(log_level=LOG_LEVEL)  # adapt if your function signature differs
logger = logging.getLogger(__name__)
logger.info("FastAPI app initialized", extra={"env": ENV})


# ----------------------------
# Middleware ordering
# ----------------------------
# Request-ID + timing first (so it wraps everything)
app.add_middleware(RequestIDAndTimingMiddleware)

# CORS next
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://your-frontend.com")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-Id"],
    allow_credentials=False,  # set True only if you use cookies + credentials
)

# GZip last (compress responses)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ----------------------------
# Routers
# ----------------------------
app.include_router(auth_router)  # keep as-is; adjust prefixes/tags in router if needed
app.include_router(items_router, prefix="/v1", tags=["items"])
app.include_router(users_router, prefix="/v1", tags=["users"])


# ----------------------------
# Custom OpenAPI Schema (Performance)
# ----------------------------
def custom_openapi():
    # If docs/openapi disabled, this won't matter.
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="High-Performance FastAPI",
        version=app.version,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema


if not IS_PROD:
    app.openapi = custom_openapi  # avoid wasted work in prod


# ----------------------------
# Optional: health endpoints
# ----------------------------
@app.get("/healthz")
async def healthz(request: Request):
    return {"ok": True, "request_id": getattr(request.state, "request_id", None)}

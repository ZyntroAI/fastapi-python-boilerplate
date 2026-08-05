"""
FastAPI application package initialization.
Handles app creation, dependency injection, and global state.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from app.core import logging as app_logging
from app.core.security import auth_router
from app.routes import items_router, users_router
from app.db.session import init_db
from app.core.rate_limiter import limiter
from app.config import settings

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(
    endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    insecure=settings.OTEL_EXPORTER_OTLP_INSECURE,
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Instrument FastAPI, SQLAlchemy, Redis, and HTTPX
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument()
RedisInstrumentor().instrument()
HTTPXClientInstrumentor().instrument()

# --- FastAPI App ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url=None if settings.PRODUCTION else "/docs",
    redoc_url=None,
    openapi_url=None if settings.PRODUCTION else "/openapi.json",
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses >1KB
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.TRUSTED_HOSTS,
)

# --- Rate Limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Include Routers ---
app.include_router(auth_router)
app.include_router(items_router, prefix="/v1", tags=["items"])
app.include_router(users_router, prefix="/v1", tags=["users"])

# --- Lifespan Events ---
@app.on_event("startup")
async def startup_event():
    await init_db()
    app_logging.setup_logging()
    print(f"✅ {settings.PROJECT_NAME} started in {'production' if settings.PRODUCTION else 'development'} mode")

@app.on_event("shutdown")
async def shutdown_event():
    print(f"🛑 {settings.PROJECT_NAME} shutting down...")

# --- Custom OpenAPI Schema ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

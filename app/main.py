import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi

from app.core import logging as app_logging
from app.core.security import auth_router
from app.routes import items_router, users_router
from app.db.session import init_db

# --- Async Lifespan for DB/Redis ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB/Redis connections
    await init_db()
    yield
    # Cleanup (e.g., close DB pools)

# --- FastAPI App ---
app = FastAPI(
    title="High-Performance FastAPI",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Disable in prod: docs_url=None
    redoc_url=None,
)

# --- Middleware ---
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress >1KB responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(auth_router)
app.include_router(items_router, prefix="/v1", tags=["items"])
app.include_router(users_router, prefix="/v1", tags=["users"])

# --- Custom OpenAPI Schema (Performance) ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="High-Performance FastAPI",
        version="1.0.0",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

# --- Logging ---
app_logging.setup_logging()
logger = logging.getLogger(__name__)
logger.info("FastAPI app initialized")

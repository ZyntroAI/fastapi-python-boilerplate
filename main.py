from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, callback, health
from app.core.config import settings

app = FastAPI(
    title="OAuth2 PKCE API",
    version="1.0.0",
    docs_url="/docs" if not settings.ENV == "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(callback.router, prefix="/auth", tags=["Auth"])
app.include_router(health.router, prefix="/health", tags=["Health"])


@app.get("/")
async def root():
    return {
        "message": "FastAPI OAuth2 PKCE",
        "environment": settings.ENV,
        "callback_url": settings.OAUTH_CALLBACK_URL,
    }

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    app.state.db = SessionLocal
    app.state.cache = {}  # Example: preload cache
    print("Resources initialized")

    yield

    # Shutdown logic
    await engine.dispose()
    app.state.cache.clear()
    print("Resources cleaned up")

app = FastAPI(lifespan=lifespan)

@app.get("/healthz")
async def health(request: Request):
    return {"db": "ok", "cache_size": len(request.state.cache)}

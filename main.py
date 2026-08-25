from fastapi import FastAPI
from app.core.security import auth_router
from app.routes import items_router, users_router
from app.routes import protected_router

app = FastAPI(title="FastAPI Example Project", version="1.0.0")

# รวมทุก router
app.include_router(auth_router)
app.include_router(items_router, prefix="/v1", tags=["items"])
app.include_router(users_router, prefix="/v1", tags=["users"])
app.include_router(protected_router)

# Health check
@app.get("/healthz", tags=["health"])
async def healthz():
    return {"ok": True, "service": "FastAPI Example Project"}
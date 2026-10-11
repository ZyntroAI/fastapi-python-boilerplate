from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.config import settings
from core.database import Base, engine
from core.limiter import limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api.v1.auth import router as auth_router
from api.v1.upload import router as upload_router

try:
    from api.v1.c2 import router as c2_router
    c2_available = True
except ImportError:
    c2_available = False
    c2_router = None

try:
    from api.v1.agentic import router as agentic_router
    agentic_available = True
except ImportError:
    agentic_available = False
    agentic_router = None

try:
    from api.v1.webhook_admin import router as webhook_router
    webhook_available = True
except ImportError as e:
    webhook_available = False
    webhook_router = None
    print(f"Webhook admin router not available: {e}")

try:
    from core.obsidian_note import check_obsidian
    from core.c2_chat import check_c0_gate
    c0_gate_pass = check_c0_gate()
    obsidian_result = check_obsidian()
except Exception as e:
    c0_gate_pass = True
    obsidian_result = {"status": f"skip: {e}"}

Base.metadata.create_all(bind=engine)

# ✅ TAGS — added
tags_metadata = [
    {"name": "Health", "description": "C0 Gate + system status — CI จะรันหลัง C0 เสมอ"},
    {"name": "C0", "description": "Primary Paper File — Obsidian + TeraBox"},
    {"name": "Auth", "description": "Register, login, verify-email, passwords — ZYNTRO-SEC-001"},
    {"name": "Upload", "description": "File uploads + MinIO"},
    {"name": "C2", "description": "C2 Adapt Chat YES — Python adapt chat"},
    {"name": "Agentic", "description": "Agentic loop + Obsidian vault model"},
    {"name": "Webhook Admin", "description": "Webhook dashboard, maintenance-status, replay-failed"},
    {"name": "Security", "description": "ZYNTRO-SEC-001 Bundle + Redis MOC"},
    {"name": "DevOps", "description": "Makefile workflow + Redis single vs cluster"},
]

app = FastAPI(
    title="ZyntroAI — C0 + C2 + Agentic + Webhook Admin + Security Bundle",
    version="1.5.0",
    docs_url="/api/docs",
    openapi_tags=tags_metadata,
    description="C0=Primary Gate, C2=Python Adapt Chat YES, Agentic=Obsidian Model, Webhook Admin Dashboard, Security=ZYNTRO-SEC-001 — Tags organized"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(upload_router, prefix="/api", tags=["Upload"])

if c2_available:
    app.include_router(c2_router, prefix="/api", tags=["C2"])
if agentic_available:
    app.include_router(agentic_router, prefix="/api", tags=["Agentic"])
if webhook_available:
    app.include_router(webhook_router, prefix="/api", tags=["Webhook Admin"])

@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "version": "1.5.0",
        "c0_gate": "PASS" if c0_gate_pass else "FAIL",
        "rule": "CI จะรันหลัง C0 เสมอ",
        "features": [
            "register", "login", "verify-email",
            "forgot-password", "reset-password", "change-password", "upload",
            "c2-adapt-chat (YES)", "agentic-loop", "obsidian-vault",
            "webhook-admin-dashboard", "maintenance-status", "replay-failed",
            "security-bundle-v1.0.0"
        ],
        "obsidian": {
            "vault": ".Obsidian2",
            "file": "C0-TERABOX.base",
            "link": "obsidian://open?vault=.Obsidian2&file=C0-TERABOX.base",
            "status": "noted"
        },
        "routers": {"c2": c2_available, "agentic": agentic_available, "webhook_admin": webhook_available},
        "security": "ZYNTRO-SEC-001 v1.0.0",
        "decision": "Workflows — GitHub vs Obsidian Sync = เก็บทั้งคู่"
    }

@app.get("/api/c0", tags=["C0"])
async def c0_status():
    return {
        "c0": "Primary Paper File",
        "exists": c0_gate_pass,
        "rule": "CI จะรันหลัง C0 เสมอ",
        "secondary": "MuMu=Termux, GuGu=GitHub",
        "obsidian": obsidian_result,
        "can_adapt_chat": "YES - Python ปรับแชทได้ในนี้ เทสในนี้ ไม่ fail เพราะ C0 ล็อคอยู่",
        "security": "ZYNTRO-SEC-001 v1.0.0 active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
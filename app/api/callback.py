# app/api/callback.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.security import generate_state  # (เผื่อคุณจะใช้ต่อในอนาคต)
from app.services.oauth_service import get_provider_endpoints
from app.services.token_service import exchange_code_for_tokens
from app.services.user_service import fetch_userinfo

router = APIRouter(prefix="/api/auth", tags=["auth"])

# NOTE:
# ตัวอย่างนี้ใช้ in-memory store เพื่อเดโมเท่านั้น
# ถ้ารันหลาย replica ใน Kubernetes ให้เปลี่ยนเป็น Redis/DB ไม่งั้น state จะหายและ callback จะล้ม
_STATE_STORE: dict[str, dict] = {}


def redirect_uri() -> str:
    return str(settings.BASE_URL).rstrip("/") + settings.OAUTH_CALLBACK_PATH


@router.get("/callback")
async def callback(code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code/state")

    entry = _STATE_STORE.get(state)
    if not entry:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    if time.time() > entry["expires_at"]:
        _STATE_STORE.pop(state, None)
        raise HTTPException(status_code=400, detail="State expired")

    verifier = entry["code_verifier"]

    endpoints = get_provider_endpoints(settings.OAUTH_PROVIDER)
    tokens = await exchange_code_for_tokens(
        token_endpoint=endpoints.token_endpoint,
        code=code,
        redirect_uri=redirect_uri(),
        code_verifier=verifier,
    )

    user = await fetch_userinfo(tokens.access_token)

    # cleanup
    _STATE_STORE.pop(state, None)

    return JSONResponse({
        "provider": settings.OAUTH_PROVIDER,
        "user": user,
        "tokens": {
            "access_token": tokens.access_token,
            "id_token": tokens.id_token,
            "expires_in": tokens.expires_in,
            "token_type": tokens.token_type,
        },
    })

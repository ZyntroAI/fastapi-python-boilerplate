import secrets
import hashlib
import base64
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.core.config import settings

router = APIRouter()


def generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge"""
    verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode("utf-8").rstrip("=")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode("utf-8").rstrip("=")
    return verifier, challenge


@router.get("/login")
async def login(request: Request):
    """Initiate OAuth2 + PKCE flow"""
    verifier, challenge = generate_pkce()
    
    # Store verifier in session/cookie (simplified - use Redis in production)
    state = secrets.token_urlsafe(16)
    
    auth_url = (
        f"{settings.OAUTH_AUTHORIZE_URL}"
        f"?client_id={settings.OAUTH_CLIENT_ID}"
        f"&redirect_uri={settings.OAUTH_CALLBACK_URL}"
        f"&response_type=code"
        f"&scope=openid email profile"
        f"&state={state}"
        f"&code_challenge={challenge}"
        f"&code_challenge_method=S256"
    )
    
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.ENV != "local",
        samesite="lax",
    )
    response.set_cookie(
        key="code_verifier",
        value=verifier,
        httponly=True,
        secure=settings.ENV != "local",
        samesite="lax",
    )
    return response

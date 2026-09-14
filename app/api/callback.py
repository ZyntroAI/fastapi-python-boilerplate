import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.services.token_service import create_jwt_token

router = APIRouter()


@router.get("/callback")
async def auth_callback(request: Request, code: str, state: str | None = None):
    """Handle OAuth2 callback and exchange code for token"""
    # Verify state
    stored_state = request.cookies.get("oauth_state")
    if stored_state and state != stored_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    verifier = request.cookies.get("code_verifier")
    if not verifier:
        raise HTTPException(status_code=400, detail="Missing code verifier")
    
    # Exchange code for access token
    token_data = {
        "client_id": settings.OAUTH_CLIENT_ID,
        "client_secret": settings.OAUTH_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.OAUTH_CALLBACK_URL,
        "grant_type": "authorization_code",
        "code_verifier": verifier,
    }
    
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(settings.OAUTH_TOKEN_URL, data=token_data)
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Token exchange failed")
        
        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        
        # Get user info
        user_resp = await client.get(
            settings.OAUTH_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_resp.json()
    
    # Create JWT for your app
    jwt_token = create_jwt_token({
        "sub": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
    })
    
    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_URL}/auth/success?token={jwt_token}"
    response = RedirectResponse(url=redirect_url)
    response.delete_cookie("oauth_state")
    response.delete_cookie("code_verifier")
    return response

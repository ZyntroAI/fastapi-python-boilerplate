from __future__ import annotations

import secrets
from urllib.parse import urlencode

import httpx

from app.core.config import settings


class OAuthService:
    def __init__(self) -> None:
        self.provider = settings.OAUTH_PROVIDER

    def create_state(self) -> str:
        return secrets.token_urlsafe(32)

    def build_authorization_url(
        self,
        state: str,
    ) -> str:
        params = {
            "client_id": settings.CLIENT_ID,
            "redirect_uri": settings.OAUTH_CALLBACK_URL,
            "response_type": "code",
            "scope": settings.OAUTH_SCOPES,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }

        return (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urlencode(params)
        )

    async def exchange_code(
        self,
        code: str,
    ) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.CLIENT_ID,
                    "client_secret": (
                        settings.CLIENT_SECRET.get_secret_value()
                    ),
                    "code": code,
                    "redirect_uri": settings.OAUTH_CALLBACK_URL,
                    "grant_type": "authorization_code",
                },
            )

            response.raise_for_status()

            return response.json()

    async def get_user_info(
        self,
        access_token: str,
    ) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )

            response.raise_for_status()

            return response.json()


oauth_service = OAuthService()

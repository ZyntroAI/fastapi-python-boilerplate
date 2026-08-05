from dataclasses import dataclass
import httpx
from typing import Any

from app.core.config import settings

@dataclass(frozen=True)
class TokenResult:
    access_token: str
    id_token: str | None
    token_type: str | None
    expires_in: int | None
    raw: Any

async def exchange_code_for_tokens(
    *,
    token_endpoint: str,
    code: str,
    redirect_uri: str,
    code_verifier: str,
) -> TokenResult:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            token_endpoint,
            data={
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        data = resp.json()

    return TokenResult(
        access_token=data.get("access_token", ""),
        id_token=data.get("id_token"),
        token_type=data.get("token_type"),
        expires_in=data.get("expires_in"),
        raw=data,
    )

import httpx
from typing import Any

from app.core.config import settings

async def fetch_userinfo(access_token: str) -> dict[str, Any]:
    # Google userinfo endpoint
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()

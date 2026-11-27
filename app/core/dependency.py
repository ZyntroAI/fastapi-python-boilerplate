from fastapi import Request
from fastapi.security import APIKeyHeader
from .config import settings
from .core.exceptions import AuthorizationError

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

async def verify_api_key(request: Request, api_key: str | None = None):
    """Dependency to verify API key for protected endpoints"""
    if not settings.API_KEY:
        # Bypass in dev if no key set
        if settings.DEBUG:
            return True
        raise AuthorizationError("API key not configured on server")

    if api_key != settings.API_KEY:
        raise AuthorizationError()

    return True

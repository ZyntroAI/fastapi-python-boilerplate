from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings


class TokenError(Exception):
    """Raised when a JWT is invalid or expired."""


def create_jwt_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **data,
        "iat": now,
        "exp": now + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "iat"]},
        )
    except ExpiredSignatureError as exc:
        raise TokenError("Token expired") from exc
    except InvalidTokenError as exc:
        raise TokenError("Invalid token") from exc
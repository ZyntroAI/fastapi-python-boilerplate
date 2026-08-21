from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings


class TokenService:
    """
    JWT access-token service.

    Responsibilities:
    - Create access tokens
    - Decode and validate access tokens

    This service does not handle:
    - OAuth provider communication
    - User database operations
    - HTTP responses
    """

    def create_access_token(
        self,
        *,
        user_id: str,
        email: str,
    ) -> str:
        now = datetime.now(timezone.utc)

        expires_at = now + timedelta(
            seconds=settings.JWT_TTL_SECONDS,
        )

        payload: dict[str, Any] = {
            "sub": user_id,
            "email": email,
            "iat": now,
            "exp": expires_at,
        }

        # Optional claims when configured.
        if settings.JWT_ISSUER:
            payload["iss"] = settings.JWT_ISSUER

        if settings.JWT_AUDIENCE:
            payload["aud"] = settings.JWT_AUDIENCE

        return jwt.encode(
            payload,
            settings.JWT_SECRET.get_secret_value(),
            algorithm=settings.JWT_ALG,
        )

    def decode_access_token(
        self,
        token: str,
    ) -> dict[str, Any]:
        options = {
            "require": [
                "sub",
                "iat",
                "exp",
            ],
        }

        kwargs: dict[str, Any] = {
            "key": settings.JWT_SECRET.get_secret_value(),
            "algorithms": [settings.JWT_ALG],
            "options": options,
        }

        if settings.JWT_ISSUER:
            kwargs["issuer"] = settings.JWT_ISSUER

        if settings.JWT_AUDIENCE:
            kwargs["audience"] = settings.JWT_AUDIENCE

        try:
            return jwt.decode(
                token,
                **kwargs,
            )

        except ExpiredSignatureError as exc:
            raise ValueError(
                "Access token has expired"
            ) from exc

        except InvalidTokenError as exc:
            raise ValueError(
                "Invalid access token"
            ) from exc


token_service = TokenService()

"""JWT auth (python-jose HS256) + bcrypt password hashing."""
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

ALGORITHM = "HS256"
TOKEN_TTL_MINUTES = int(os.environ.get("JWT_TTL_MINUTES", "120"))

# A signing key shorter than this is rejected outright.
MIN_SECRET_LENGTH = 32

# Values that must never be accepted as a real signing key.
_INSECURE_SECRETS = {
    "changeme",
    "change-me",
    "change_me",
    "secret",
    "password",
    "test",
    "jwt-secret",
    "jwt_secret",
    "dev-insecure-secret-change-me",
    "replace-me-with-a-48-byte-random-secret",
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)


def _validate_secret(value: str) -> str:
    """Reject weak or placeholder JWT secrets.

    Called on any secret that arrives from the environment, so a misconfigured
    deployment fails loudly instead of signing tokens with a guessable key.
    """
    if len(value) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"JWT_SECRET must be at least {MIN_SECRET_LENGTH} characters "
            f"(got {len(value)}). Generate one with: "
            'python -c "import secrets; print(secrets.token_urlsafe(48))"'
        )
    if value.strip().lower() in _INSECURE_SECRETS:
        raise RuntimeError("JWT_SECRET is a known insecure placeholder value.")
    return value


def _secret() -> str:
    """Return the signing key.

    Prefers JWT_SECRET from the environment (validated). Falls back to a
    generated key file for local development so the app boots out of the box —
    the generated key is always full-strength.
    """
    secret = os.environ.get(settings.jwt_secret_env)
    if secret:
        return _validate_secret(secret)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    keyfile = settings.data_dir / "jwt_secret.txt"
    if keyfile.exists():
        return keyfile.read_text().strip()
    k = secrets.token_hex(32)
    keyfile.write_text(k)
    return k


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> str:
    payload = jwt.decode(token, _secret(), algorithms=[ALGORITHM])
    sub = payload.get("sub")
    if not sub:
        raise JWTError("missing subject")
    return sub


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")
    try:
        return decode_token(creds.credentials)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")

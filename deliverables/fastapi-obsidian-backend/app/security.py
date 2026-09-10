"""JWT auth (python-jose HS256) + bcrypt password hashing."""
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

ALGORITHM = "HS256"
TOKEN_TTL_MINUTES = int(os.environ.get("JWT_TTL_MINUTES", "120"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)


def _secret() -> str:
    secret = os.environ.get(settings.jwt_secret_env)
    if secret:
        return secret
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    keyfile = settings.data_dir / "jwt_secret.txt"
    if keyfile.exists():
        return keyfile.read_text().strip()
    import secrets
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

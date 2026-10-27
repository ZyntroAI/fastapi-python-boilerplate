"""
Security utilities — JWT, password hashing, token management
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import hashlib
import hmac
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.utils.datetime import utc_now

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password securely"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(
    data: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: Optional[int] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = utc_now()
    if expires_delta:
        expire += expires_delta
    elif expires_minutes:
        expire += timedelta(minutes=expires_minutes)
    else:
        expire += timedelta(minutes=15)

    to_encode.update({"exp": expire, "iat": utc_now()})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_jwt(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT, returns None if invalid"""
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None


def generate_secret(length: int = 32) -> str:
    """Generate cryptographically secure secret string"""
    return secrets.token_hex(length // 2)


def hmac_sign(
    payload: Union[str, bytes],
    key: Union[str, bytes],
    algorithm: str = "sha256",
) -> str:
    """Create HMAC signature"""
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    if isinstance(key, str):
        key = key.encode("utf-8")
    return hmac.new(key, payload, getattr(hashlib, algorithm)).hexdigest()


def hmac_verify(
    payload: Union[str, bytes],
    signature: str,
    key: Union[str, bytes],
    algorithm: str = "sha256",
) -> bool:
    """Verify HMAC signature safely"""
    expected = hmac_sign(payload, key, algorithm)
    return hmac.compare_digest(expected, signature)

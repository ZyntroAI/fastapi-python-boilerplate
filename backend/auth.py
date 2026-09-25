from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

Role = Literal["admin", "user"]

class TokenPayload(BaseModel):
    sub: str
    role: Role
    exp: int

def create_access_token(*, subject: str, role: Role) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.token_exp_minutes)
    payload = {"sub": subject, "role": role, "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        # payload["sub"], payload["role"], payload["exp"] should exist
        return {"id": payload["sub"], "role": payload["role"]}
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_role(required: Role):
    async def _checker(user=Depends(get_current_user)):
        if user["role"] != required:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user
    return _checker

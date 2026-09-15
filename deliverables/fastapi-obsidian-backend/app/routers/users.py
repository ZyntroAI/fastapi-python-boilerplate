"""Users - register + login returning JWT tokens, backed by the user database."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..security import create_access_token, hash_password, verify_password
from ..user_store import user_store

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    allowed_skills: list[str] | None = None


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn):
    username = body.username.strip()
    if user_store.exists(username):
        raise HTTPException(status_code=409, detail="username already exists")
    user_store.create(
        username,
        hash_password(body.password),
        allowed_skills=body.allowed_skills,
    )
    return TokenOut(access_token=create_access_token(username))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    record = user_store.get(body.username.strip())
    if not record or not verify_password(body.password, record["hashed_password"]):
        raise HTTPException(status_code=401, detail="invalid username or password")
    return TokenOut(access_token=create_access_token(record["username"]))

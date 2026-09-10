"""Users - register + login returning JWT tokens."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import db
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    username: str
    password: str


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn):
    users = db.get("users", {})
    if body.username in users:
        raise HTTPException(status_code=409, detail="username already exists")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="password must be at least 6 chars")
    users[body.username] = {"hashed_password": hash_password(body.password)}
    db.set("users", users)
    return TokenOut(access_token=create_access_token(body.username))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    users = db.get("users", {})
    record = users.get(body.username)
    if not record or not verify_password(body.password, record["hashed_password"]):
        raise HTTPException(status_code=401, detail="invalid username or password")
    return TokenOut(access_token=create_access_token(body.username))

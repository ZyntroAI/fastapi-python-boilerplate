from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# ──────────────────────────────────────────────
# Token Schemas
# ──────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = Field(default_factory=list)
    exp: Optional[datetime] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ──────────────────────────────────────────────
# User Schemas
# ──────────────────────────────────────────────
class User(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: bool = False
    scopes: list[str] = Field(default_factory=list)  # e.g., ["me", "admin"]


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str]
    disabled: bool
    scopes: list[str]

    class Config:
        from_attributes = True  # Works with ORM models

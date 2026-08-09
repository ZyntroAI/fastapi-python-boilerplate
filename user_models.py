from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

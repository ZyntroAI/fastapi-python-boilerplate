from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
import jwt
import time

router = APIRouter(prefix="/auth", tags=["auth"])

# ตัวอย่าง secret key สำหรับ JWT
SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

# จำลองฐานข้อมูลผู้ใช้
users_db = {}

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def hash_password(password: str) -> str:
    """แฮชรหัสผ่านด้วย SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username: str) -> str:
    """สร้าง JWT token"""
    payload = {
        "sub": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600  # หมดอายุใน 1 ชั่วโมง
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register(user: UserRegister):
    """สมัครสมาชิกใหม่"""
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[user.username] = hash_password(user.password)
    return {"msg": "User registered successfully"}

@router.post("/login")
async def login(user: UserLogin):
    """เข้าสู่ระบบ"""
    hashed = users_db.get(user.username)
    if not hashed or hashed != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.username)
    return {"access_token": token, "token_type": "bearer"}
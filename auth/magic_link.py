# auth/magic_link.py
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from .database import DBUser
from .email import send_email
from .jwt import create_access_token
import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
MAGIC_LINK_EXPIRE_MINUTES = 15

def create_magic_link(db: Session, email: str, ip: str, user_agent: str) -> str:
    """สร้างลิงก์ล็อกอิน"""
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        # ไม่บอกว่ามีหรือไม่มี เพื่อความปลอดภัย
        return ""
    
    token_id = uuid.uuid4().hex
    expiry = datetime.utcnow() + timedelta(minutes=MAGIC_LINK_EXPIRE_MINUTES)
    
    # บันทึก token short-lived
    from .database import MagicLinkToken
    db.add(MagicLinkToken(
        id=token_id,
        user_id=user.id,
        expires_at=expiry,
        ip_address=ip,
        user_agent=user_agent
    ))
    db.commit()
    
    link = f"{FRONTEND_URL}/auth/verify-magic?token={token_id}"
    
    # ส่งอีเมล
    send_email(
        to_email=user.email,
        subject="🔗 เข้าสู่ระบบ ZyntroAI",
        html_content=f"""
        <div style="font-family:sans-serif;max-width:500px;padding:20px;">
            <h2>เข้าสู่ระบบ ZyntroAI</h2>
            <p>กดปุ่มด้านล่างเพื่อล็อกอิน — ลิงก์หมดอายุใน {MAGIC_LINK_EXPIRE_MINUTES} นาที</p>
            <a href="{link}" style="display:inline-block;background:#3b82f6;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">
                ✅ เข้าสู่ระบบทันที
            </a>
            <p style="margin-top:20px;font-size:12px;color:#888;">
                หากไม่ได้ขอลิงก์นี้ — เพียงแค่ละเลยอีเมลนี้
            </p>
        </div>
        """
    )
    
    return token_id

import os
import httpx
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from .database import DBUser, DBSession
import logging

logger = logging.getLogger("zyntroai.push")

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "")
FCM_URL = "https://fcm.googleapis.com/fcm/send"

# ------------------------------
# โมเดล — เพิ่มใน database.py
# ------------------------------
"""
class FCMDevice(Base):
    __tablename__ = "fcm_devices"
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False)
    device_name = Column(String(100))
    platform = Column(String(20))  # android / ios / web
    locale = Column(String(10), default="th")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
"""

# ------------------------------
# ฟังก์ชันหลัก
# ------------------------------
async def send_push(
    fcm_token: str,
    title: str,
    body: str,
    data: dict = None,
    priority: str = "high"
) -> bool:
    """ส่ง Push Notification ไปยังอุปกรณ์เครื่องเดียว"""
    if not FCM_SERVER_KEY or not fcm_token:
        return False
    
    payload = {
        "to": fcm_token,
        "notification": {
            "title": title,
            "body": body,
            "sound": "default",
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        },
        "data": data or {},
        "priority": priority
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.post(
            FCM_URL,
            headers={
                "Authorization": f"key={FCM_SERVER_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        return res.status_code == 200

async def send_push_to_user(
    db: Session,
    user_id: str,
    title: str,
    body: str,
    data: dict = None
) -> int:
    """ส่งให้ทุกอุปกรณ์ที่ผู้ใช้มี"""
    from .database import FCMDevice
    devices = db.query(FCMDevice).filter(FCMDevice.user_id == user_id).all()
    sent = 0
    for dev in devices:
        if await send_push(dev.token, title, body, data):
            sent += 1
    return sent

# ------------------------------
# เส้นทาง API
# ------------------------------
"""
@router.post("/register-device")
async def register_device(
    token: str = Body(...),
    device_name: str = Body(None),
    platform: str = Body(...),
    locale: str = Body("th"),
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    # ลบ token เก่าถ้ามี
    db.query(FCMDevice).filter(FCMDevice.token == token).delete()
    # เพิ่มใหม่
    dev = FCMDevice(
        id=f"fcm_{uuid.uuid4().hex[:12]}",
        user_id=user.sub,
        token=token,
        device_name=device_name,
        platform=platform,
        locale=locale
    )
    db.add(dev)
    db.commit()
    return {"success": True, "message": "ลงทะเบียนอุปกรณ์สำเร็จ"}
"""

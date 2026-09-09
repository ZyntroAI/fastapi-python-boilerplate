"""Celery app — ตั้งค่าคิวงาน background"""
from celery import Celery

from app.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "firecrawl_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,      # งานยืนยันเมื่อเสร็จ ไม่ใช่ตอนรับ — รองรับ retry หลัง crash
    worker_prefetch_multiplier=1,
    task_time_limit=300,      # 5 นาที กันงานค้าง
    task_soft_time_limit=270,
    result_expires=3600,
)

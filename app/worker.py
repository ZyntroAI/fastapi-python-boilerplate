# app/worker.py
import os
from celery import Celery

celery_app = Celery("crystalcastle")
celery_app.conf.update(
    broker_url=os.environ["CELERY_BROKER_URL"],
    result_backend=os.environ["CELERY_RESULT_BACKEND"],
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Bangkok",
    task_track_started=True,
    task_acks_late=True,                 # ยอมรับหลังทำเสร็จ กระทะได้ถ้า worker ตาย
    worker_prefetch_multiplier=1,        # เหมาะกับ task หนัก
    beat_schedule={                     # ถ้าใช้ celery-beat (--profile beat)
        "cleanup-uploads-every-midnight": {
            "task": "app.worker.cleanup_old_uploads",
            "schedule": 3600.0 * 24,
        },
    },
)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, to: str, subject: str, body: str):
    try:
        # ... ส่งอีเมล / เรียก API ภายนอก / ประมวลผลหนักๆ ...
        return {"ok": True, "to": to}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)  # exponential backoff

@celery_app.task
def cleanup_old_uploads():
    # ... ลบไฟล์เก่า ...
    pass

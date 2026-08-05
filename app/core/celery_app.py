# app/core/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "fastapi_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task
def send_email_async(to: str, subject: str, body: str):
    # Simulate email sending
    import time
    time.sleep(2)  # Simulate I/O
    print(f"Email sent to {to}: {subject}")

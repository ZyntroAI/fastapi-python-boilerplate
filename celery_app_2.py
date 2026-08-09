from app.core.celery_app import send_email_async

@router.post("/send-email")
async def send_email(email: str, subject: str):
    send_email_async.delay(email, subject, "Hello!")
    return {"status": "queued"}

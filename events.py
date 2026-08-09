# app/routes/events.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()

async def event_stream():
    for i in range(10):
        await asyncio.sleep(1)
        yield f"data: Message {i}\n\n"

@router.get("/stream")
async def stream_events():
    return StreamingResponse(event_stream(), media_type="text/event-stream")

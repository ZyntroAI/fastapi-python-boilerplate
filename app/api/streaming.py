import json
from typing import AsyncGenerator

from fastapi.responses import StreamingResponse

async def sse_events() -> AsyncGenerator[bytes, None]:
    for i in range(5):
        payload = {"event": "tick", "i": i}
        yield f"data: {json.dumps(payload)}\n\n".encode("utf-8")
        import asyncio
        await asyncio.sleep(0.4)

def sse_response():
    return StreamingResponse(sse_events(), media_type="text/event-stream")

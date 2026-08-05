import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.perf_counter()

        response: Response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["x-request-id"] = request_id
        response.headers["x-elapsed-ms"] = f"{elapsed_ms:.2f}"
        return response

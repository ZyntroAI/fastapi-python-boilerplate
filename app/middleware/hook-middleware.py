import time
from fastapi import Request, Response


class HookMiddleware:
    async def __call__(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = round(time.perf_counter() - start, 4)
        response.headers["X-Process-Time"] = str(duration)
        return response

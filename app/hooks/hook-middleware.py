import time from fastapi import Request

class HookMiddleware: async def call(self, request: Request, call_next): start = time.time() response = await call_next(request) duration = round(time.time() - start, 4) response.headers["X-Process-Time"] = str(duration) return response

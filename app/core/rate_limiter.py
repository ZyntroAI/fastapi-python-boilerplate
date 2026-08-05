# app/core/rate_limiter.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda r, e: HTTPException(
    status_code=429,
    detail=f"Too many requests. Retry in {e.detail['retry_after']} seconds.",
))

# Apply to all routes
@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(response.headers.get("X-RateLimit-Remaining", 100))
    return response

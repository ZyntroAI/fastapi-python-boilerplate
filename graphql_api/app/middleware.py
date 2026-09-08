"""Auth helpers used by resolvers + a cache decorator.

Note: strawberry schema resolvers already receive context["user"] from our
context_getter (main.py). This module adds a role guard decorator and an
async Redis cache decorator keyed by function+args.
"""
from __future__ import annotations

import hashlib
import json
from functools import wraps
from typing import Any, Callable

from strawberry.types import Info

from app.errors import AuthenticationRequired, PermissionDenied
from app.redis import redis_pubsub


def requires_role(role: str):
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        async def wrapper(info: Info, *args: Any, **kwargs: Any) -> Any:
            user = info.context.get("user")
            if not user:
                raise AuthenticationRequired()
            if user.get("role") != role:
                raise PermissionDenied()
            return await f(info, *args, **kwargs)
        return wrapper
    return decorator


def cache_resolver(ttl: int = 60):
    """Cache an async resolver's return (must be JSON-serializable) in Redis."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # stable key: fn name + sha1 of repr(arguments)
            raw = repr(args) + repr(kwargs)
            digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()
            key = f"gql:cache:{f.__name__}:{digest}"
            hit = await redis_pubsub.get(key)
            if hit is not None:
                return json.loads(hit)
            result = await f(*args, **kwargs)
            await redis_pubsub.setex(key, ttl, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

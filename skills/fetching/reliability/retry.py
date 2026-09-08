"""Async retry with exponential backoff + optional predicate."""
from __future__ import annotations

import asyncio
from functools import wraps
from typing import Callable


def retry(max_attempts: int = 3, backoff: float = 1.0, on: Callable[[Exception], bool] = lambda e: True):
    def deco(f):
        @wraps(f)
        async def wrap(*args, **kw):
            last = None
            for i in range(max_attempts):
                try:
                    return await f(*args, **kw)
                except Exception as e:  # noqa: BLE001 - retry boundary
                    last = e
                    if not on(e) or i == max_attempts - 1:
                        raise
                    await asyncio.sleep(backoff * (2 ** i))
            raise last  # pragma: no cover
        return wrap
    return deco

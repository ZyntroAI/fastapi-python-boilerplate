"""Resilience: bounded retry with exponential backoff.

Unlike the naive decorator this replaces, the **original** exception is what
propagates once the budget is spent — a caller that wants to inspect
``err.status`` still can.  We never swallow the real error behind a generic
``RuntimeError``.
"""
from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, TypeVar

from .errors import AgentAPIError, AgentRateLimitError, AgentTimeoutError

T = TypeVar("T")

#: Errors worth retrying: transient server faults, rate limits, timeouts.
RETRYABLE = (AgentRateLimitError, AgentTimeoutError)


def _is_retryable(err: BaseException) -> bool:
    if isinstance(err, RETRYABLE):
        return True
    # 5xx are server-side/transient; 4xx are our fault and must not loop.
    return isinstance(err, AgentAPIError) and err.status >= 500


async def with_retry(
    call: Callable[[], Awaitable[T]],
    *,
    retries: int = 3,
    base_delay: float = 1.0,
    sleep: Callable[[float], Awaitable[None]] | None = None,
    on_retry: Callable[[int, BaseException, float], None] | None = None,
) -> T:
    """Run ``call`` up to ``retries`` times, backing off between attempts.

    ``sleep`` and ``on_retry`` are injectable so tests never actually wait.
    ``sleep`` resolves at call time (not as a bound default) so it can also be
    monkeypatched.
    """
    if retries < 1:
        raise ValueError("retries must be >= 1")
    if sleep is None:
        sleep = asyncio.sleep

    last: BaseException | None = None
    for attempt in range(retries):
        try:
            return await call()
        except BaseException as err:  # noqa: BLE001 - re-raised below
            if not _is_retryable(err):
                raise
            last = err
            if attempt == retries - 1:
                break
            delay = base_delay * (2**attempt)
            if on_retry is not None:
                on_retry(attempt + 1, err, delay)
            await sleep(delay)

    assert last is not None  # loop only exits with an error recorded
    raise last

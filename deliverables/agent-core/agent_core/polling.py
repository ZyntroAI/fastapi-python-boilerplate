"""Task polling — bounded, never an infinite hang."""
from __future__ import annotations

import asyncio
import time
from typing import Any, Callable

from .base import TERMINAL_STATUSES, TargetClient
from .config import get_settings
from .errors import AgentPollTimeoutError
from .schemas import AgentTaskResult


async def poll_task(
    task_id: str,
    client: TargetClient,
    *,
    interval: float | None = None,
    timeout: float | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> AgentTaskResult:
    """Poll ``task_id`` until it reaches a terminal state or the budget runs out.

    A task stuck in ``running`` forever used to hang the request; now it raises
    :class:`AgentPollTimeoutError` instead.  ``clock`` is injectable so tests
    run instantly.
    """
    settings = get_settings()
    interval = interval if interval is not None else settings.AGENT_POLL_INTERVAL
    timeout = timeout if timeout is not None else settings.AGENT_POLL_TIMEOUT

    started = clock()
    last_status = "unknown"

    while True:
        last_status = await client.status(task_id)
        if last_status in TERMINAL_STATUSES:
            result: dict[str, Any] | None = None
            if last_status == "completed":
                result = await client.result(task_id)
            return AgentTaskResult(
                task_id=task_id, status=last_status, result=result
            )

        if clock() - started >= timeout:
            raise AgentPollTimeoutError(task_id, last_status, timeout)

        await asyncio.sleep(interval)

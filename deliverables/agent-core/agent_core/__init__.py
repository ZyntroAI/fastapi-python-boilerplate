"""Agent Core — provider-agnostic agent task backend.

Public surface::

    from agent_core import AgentClient, poll_task, get_settings

Configuration is resolved lazily, so importing this package needs no
credentials.  Call :func:`get_settings` (or construct a client) when you
actually need them.
"""
from .base import TERMINAL_STATUSES, TargetClient
from .client import AgentClient
from .config import Settings, get_settings
from .db import TaskStore
from .errors import (
    AgentAPIError,
    AgentAuthError,
    AgentConfigError,
    AgentError,
    AgentPollTimeoutError,
    AgentRateLimitError,
    AgentTimeoutError,
)
from .polling import poll_task
from .retry import with_retry
from .schemas import AgentSubmit, AgentTaskOut, AgentTaskResult, HealthOut

__version__ = "1.0.0"

__all__ = [
    "AgentAPIError",
    "AgentAuthError",
    "AgentClient",
    "AgentConfigError",
    "AgentError",
    "AgentPollTimeoutError",
    "AgentRateLimitError",
    "AgentSubmit",
    "AgentTaskOut",
    "AgentTaskResult",
    "AgentTimeoutError",
    "HealthOut",
    "Settings",
    "TERMINAL_STATUSES",
    "TargetClient",
    "TaskStore",
    "get_settings",
    "poll_task",
    "with_retry",
]

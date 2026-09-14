"""Hierarchical, actionable exceptions for Agent Core."""
from __future__ import annotations


class AgentError(Exception):
    """Base class for every Agent Core error."""


class AgentConfigError(AgentError):
    """Required configuration (e.g. the API key) is missing."""


class AgentAuthError(AgentError):
    """Provider rejected our credentials (401/403)."""


class AgentRateLimitError(AgentError):
    """Provider rate-limited the call (429). Retryable."""


class AgentTimeoutError(AgentError):
    """The provider did not answer within the configured timeout."""


class AgentAPIError(AgentError):
    """Provider returned a non-2xx response that is not one of the above."""

    def __init__(self, status: int, detail: str) -> None:
        self.status = status
        self.detail = detail
        super().__init__(f"API error {status}: {detail}")


class AgentPollTimeoutError(AgentError):
    """A task never reached a terminal state inside the polling budget."""

    def __init__(self, task_id: str, last_status: str, timeout: float) -> None:
        self.task_id = task_id
        self.last_status = last_status
        self.timeout = timeout
        super().__init__(
            f"task {task_id} still '{last_status}' after {timeout}s"
        )

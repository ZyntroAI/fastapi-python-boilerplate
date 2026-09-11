"""Circuit breaker — Closed / Open / Half-Open state machine."""
from __future__ import annotations

import time
from typing import Optional


class CircuitBreaker:
    """Circuit breaker state machine.

    - CLOSED:    allow requests normally
    - OPEN:      failure threshold exceeded → block all for the cooldown
    - HALF_OPEN: after cooldown, allow one probe — success→CLOSED, failure→OPEN
    """

    def __init__(self, failure_threshold: int = 5, recovery_seconds: float = 30.0) -> None:
        self.failure_threshold = max(1, failure_threshold)
        self.recovery_seconds = max(0.1, recovery_seconds)
        self._failures = 0
        self._state = "CLOSED"
        self._opened_at: Optional[float] = None

    @property
    def state(self) -> str:
        if self._state == "OPEN" and self._opened_at is not None:
            if time.monotonic() - self._opened_at >= self.recovery_seconds:
                self._state = "HALF_OPEN"
        return self._state

    def allow_request(self) -> bool:
        s = self.state
        if s == "CLOSED":
            return True
        if s == "OPEN":
            return False
        # HALF_OPEN — allow one probe
        return True

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None
        self._state = "CLOSED"

    def record_failure(self) -> None:
        if self.state == "HALF_OPEN":
            self._open()
            return
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._open()

    def _open(self) -> None:
        self._state = "OPEN"
        self._opened_at = time.monotonic()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CircuitBreaker {self._state} failures={self._failures}>"

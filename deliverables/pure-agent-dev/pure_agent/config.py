"""Central configuration — provider selection lives here, not in the agents."""

from __future__ import annotations

import os
from enum import StrEnum


class ProviderName(StrEnum):
    MOCK = "mock"
    BYTEPLUS = "byteplus"


def selected_provider() -> ProviderName:
    """Which adapter the app wires up. Defaults to mock so the app always boots."""
    raw = os.getenv("COMPUTE_PROVIDER", ProviderName.MOCK.value).strip().lower()
    try:
        return ProviderName(raw)
    except ValueError as exc:
        valid = ", ".join(p.value for p in ProviderName)
        raise ValueError(f"COMPUTE_PROVIDER must be one of: {valid} (got {raw!r})") from exc

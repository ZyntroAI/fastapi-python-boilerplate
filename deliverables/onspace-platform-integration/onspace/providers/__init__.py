"""Provider abstraction — contract, error model, and concrete providers.

`providers/` is intentionally a package so adding a vendor means adding one
module and registering it; the router never changes.
"""
from __future__ import annotations

from .base import BaseProvider, ProviderError, ProviderResult, RETRYABLE_STATUS, NON_RETRYABLE_STATUS
from .mock import MockProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .google import GoogleProvider

__all__ = [
    "BaseProvider",
    "ProviderError",
    "ProviderResult",
    "RETRYABLE_STATUS",
    "NON_RETRYABLE_STATUS",
    "MockProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "GoogleProvider",
]

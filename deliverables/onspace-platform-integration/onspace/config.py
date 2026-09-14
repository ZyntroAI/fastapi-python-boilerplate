"""OnSpaceAI configuration.

Env-prefixed (`ONSPACE_`) and self-contained so the AI infrastructure layer
never has to depend on the core app's settings (which require OAuth
credentials the AI layer does not need).
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class OnSpaceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ONSPACE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "OnSpaceAI"
    app_env: str = "development"

    # Redis (optional — falls back to in-memory cache when not configured)
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300

    # Circuit breaker
    circuit_failure_threshold: int = 5
    circuit_recovery_seconds: float = 30.0

    # Token budget
    token_max: int = 128000
    model_default: str = "gpt-4o"

    # Provider API keys (read from env — never hardcoded)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Auth
    api_key: str = ""


@lru_cache
def get_onspace_settings() -> OnSpaceSettings:
    return OnSpaceSettings()

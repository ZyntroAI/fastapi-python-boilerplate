"""Type-safe configuration.

Settings are created lazily through ``get_settings()`` so that simply
**importing** the package never requires credentials to be present.  This is
what lets the test suite (and any library consumer) import Agent Core in an
environment with no ``.env``.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from .errors import AgentConfigError


class Settings(BaseSettings):
    """Centralized app settings, loaded from environment variables / ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Agent provider -------------------------------------------------
    AGENT_PROVIDER: str = "agent"
    AGENT_BASE_URL: str = "https://api.agent.ai/v2"
    AGENT_API_KEY: str = ""
    AGENT_TIMEOUT: float = 120.0
    AGENT_MAX_RETRIES: int = 3
    AGENT_POLL_INTERVAL: float = 2.0
    AGENT_POLL_TIMEOUT: float = 300.0

    # --- Supabase (optional until persistence is used) ------------------
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    def require_api_key(self) -> str:
        """Return the API key or fail loudly — never send an empty header."""
        if not self.AGENT_API_KEY:
            raise AgentConfigError(
                "AGENT_API_KEY is not set (env var or .env); refusing to call "
                "the provider without credentials"
            )
        return self.AGENT_API_KEY

    def require_supabase(self) -> tuple[str, str]:
        if not self.SUPABASE_URL or not self.SUPABASE_SERVICE_KEY:
            raise AgentConfigError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must both be set to use "
                "the task store"
            )
        return self.SUPABASE_URL.rstrip("/"), self.SUPABASE_SERVICE_KEY


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings singleton, built on first use."""
    return Settings()

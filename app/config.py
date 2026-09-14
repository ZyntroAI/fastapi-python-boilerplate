"""App settings — thin config used by several modules.

Note: this file lives alongside app/core/config.py (the fuller settings
source). It is imported directly by env.py, core/security.py, core/performance.py
and tests. It must import BaseSettings (was missing) and expose the fields those
consumers reference plus a `settings` singleton.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "production"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    # JWT
    JWT_SECRET_KEY: str = "super-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Sentry / cache / misc
    SENTRY_DSN: str | None = None
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300

    # Central Credential Broker (metadata-only)
    CREDENTIAL_BROKER_URL: str | None = None
    BROKER_TOKEN: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()

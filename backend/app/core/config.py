"""Application settings — type-safe env config.

Faithful to the merged spec: app identity, environment, database, redis,
JWT auth and the optional Algolia/Obsidian credentials. Loaded once and cached.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_name: str = "ZyntroAI API"
    environment: str = "development"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://user:pass@db:5432/zyntro"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "change_this_in_prod"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    algolia_app_id: str | None = None
    algolia_api_key: str | None = None
    obsidian_api_token: str | None = None
    obsidian_api_url: str | None = None

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Settings — SECRET_KEY comes from env; no default secret in code."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "GraphQL API"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite+aiosqlite:///./graphql.db"  # dev default; override via env
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SUB_CHANNEL: str = "graphql:events"
    SECRET_KEY: str = "dev-only-change-me"   # MUST override in production env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

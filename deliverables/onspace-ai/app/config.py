"""การตั้งค่า OnSpaceAI — โหลดจาก .env ด้วย pydantic-settings"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "OnSpaceAI"
    app_env: str = "development"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300

    # Circuit breaker
    circuit_failure_threshold: int = 5
    circuit_recovery_seconds: float = 30.0

    # Token budget
    token_max: int = 128000
    model_default: str = "gpt-4o"

    # Provider API keys (อ่านจาก env — ไม่ hardcode)
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Auth
    api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()

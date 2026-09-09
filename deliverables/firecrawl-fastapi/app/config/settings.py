"""การตั้งค่าแอป — โหลดจาก .env ด้วย pydantic-settings"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FireCrawl FastAPI"
    app_env: str = "development"
    debug: bool = False

    # FireCrawl
    firecrawl_api_key: str = ""
    firecrawl_base_url: str = "https://api.firecrawl.dev"
    firecrawl_timeout: int = 30
    firecrawl_retries: int = 3

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_url: str = "redis://localhost:6379/1"

    # Cache TTL (วินาที)
    cache_ttl_scrape: int = 600
    cache_ttl_crawl: int = 1800

    # Rate limit (คำขอ/นาที)
    rate_limit_scrape: int = 120
    rate_limit_crawl: int = 60

    # Webhook
    webhook_secret: str = ""

    # Celery
    celery_broker_url: str = "redis://localhost:6379/2"
    celery_result_backend: str = "redis://localhost:6379/3"

    # Logging
    log_format: str = "json"  # json | console


@lru_cache
def get_settings() -> Settings:
    return Settings()

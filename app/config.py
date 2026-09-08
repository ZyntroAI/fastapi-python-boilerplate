class Settings(BaseSettings):
    # ... existing ...
    REDIS_URL: str = "redis://localhost:6379/0"
    SENTRY_DSN: str
    ENV: str = "production"
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300

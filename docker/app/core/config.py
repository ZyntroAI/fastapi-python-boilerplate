from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Priority: env > .env > defaults
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # discard unknown keys → faster parse
        case_sensitive=False,
    )

    app_name: str = "ZyntroAI"
    debug: bool = False
    api_timeout: int = 30
    redis_url: str = "redis://localhost:6379/0"

@lru_cache(maxsize=1)  # ✅ SINGLETON — parse ONCE
def get_settings() -> Settings:
    return Settings()
 
 
- Why:  lru_cache  ensures config parsed once → no repeated I/O/parsing
- Load time: ~1–3ms vs ~20–50ms per repeated load
 
2. Redis-Backed Dynamic Config (for multi-agent)
 
python
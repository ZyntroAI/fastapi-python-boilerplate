import redis.asyncio as redis
from pydantic import BaseModel
from typing import Optional
import json

class DynamicConfig(BaseModel):
    agent_timeout: int = 120
    max_concurrent_tasks: int = 50
    cache_ttl_sec: int = 300

class CachedConfigRepo:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self._local: Optional[DynamicConfig] = None
        self._etag: str = ""

    async def get(self) -> DynamicConfig:
        # Check local cache first
        if self._local:
            return self._local
        # Redis fetch with 1min refresh window
        data = await self.redis.get("global:config")
        if data:
            self._local = DynamicConfig(**json.loads(data))
            return self._local
        # Fallback defaults
        return DynamicConfig()

    async def refresh(self) -> None:
        self._local = None  # invalidate
 
 
- Local in-memory + Redis = sub-ms read performance
- Avoids Git repo polling overhead at runtime
 
3. Gunicorn/Uvicorn — Worker Tuning
 
python
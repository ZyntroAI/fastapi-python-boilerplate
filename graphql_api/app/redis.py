"""Redis async client + Pub/Sub. Tolerates an unreachable Redis (never breaks
the GraphQL server when Redis is down)."""
import json
from typing import Any, AsyncGenerator, Dict, Optional

import redis.asyncio as aioredis

from app.config import settings


class RedisPubSub:
    def __init__(self) -> None:
        self._client: Optional[aioredis.Redis] = None

    def _get(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
        return self._client

    async def publish(self, channel: str, message: Dict[str, Any]) -> None:
        try:
            await self._get().publish(channel, json.dumps(message))
        except Exception:
            pass  # Redis down: no-op, don't break the request

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self._get().get(key)
        except Exception:
            return None

    async def setex(self, key: str, ttl: int, value: str) -> None:
        try:
            await self._get().setex(key, ttl, value)
        except Exception:
            pass

    async def subscribe(self, channel: str) -> AsyncGenerator[Dict[str, Any], None]:
        pubsub = self._get().pubsub()
        await pubsub.subscribe(channel)
        try:
            async for raw in pubsub.listen():
                if raw and raw.get("type") == "message":
                    data = raw.get("data")
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    try:
                        yield json.loads(data) if isinstance(data, str) else data
                    except (TypeError, json.JSONDecodeError):
                        yield {"raw": data}
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()


redis_pubsub = RedisPubSub()

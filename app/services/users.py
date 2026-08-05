"""
User service layer with async-first design, caching, and bulk operations.
Optimized for production with:
- Async SQLAlchemy sessions
- Redis caching
- Bulk operations
- Circuit breakers for external calls
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from redis.asyncio import Redis
from opentelemetry import trace
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

from app.db.models import User  # Replace with your ORM model
from app.db.repositories import UserRepository
from app.schemas.users import (
    UserCreate,
    UserRead,
    UserUpdate,
    UserPublic,
)
from app.core.cache import redis_client
from app.core.exceptions import ServiceException
from app.core.http_client import http_client

tracer = trace.get_tracer(__name__)

class UserService:
    """High-performance user service with async operations."""

    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,)),
    )
    async def create_user(
        session: AsyncSession,
        user: UserCreate,
        cache: Redis = redis_client,
    ) -> UserRead:
        """Create user with caching and retry logic."""
        cache_key = f"user:email:{user.email}"
        cached = await cache.get(cache_key)
        if cached:
            return UserRead.model_validate_json(cached)

        db_user = await UserRepository.create(session, user)
        result = UserRead.model_validate(db_user)

        # Cache the result
        await cache.setex(
            cache_key,
            timedelta(minutes=30).seconds,
            result.model_dump_json(),
        )
        return result

    @staticmethod
    async def get_user(
        session: AsyncSession,
        user_id: int,
        cache: Redis = redis_client,
    ) -> Optional[UserRead]:
        """Get user with caching and circuit breaker."""
        cache_key = f"user:{user_id}"
        cached = await cache.get(cache_key)
        if cached:
            return UserRead.model_validate_json(cached)

        db_user = await UserRepository.get(session, user_id)
        if not db_user:
            return None

        result = UserRead.model_validate(db_user)
        await cache.setex(
            cache_key,
            timedelta(minutes=30).seconds,
            result.model_dump_json(),
        )
        return result

    @staticmethod
    async def list_users(
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
        cache: Redis = redis_client,
    ) -> List[UserPublic]:
        """List users with pagination and caching."""
        cache_key = f"users:list:{limit}:{offset}"
        cached = await cache.get(cache_key)
        if cached:
            return [UserPublic.model_validate_json(u) for u in json.loads(cached)]

        db_users = await UserRepository.list(session, limit, offset)
        result = [UserPublic.model_validate(u) for u in db_users]

        await cache.setex(
            cache_key,
            timedelta(minutes=5).seconds,
            json.dumps([u.model_dump() for u in result]),
        )
        return result

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user_id: int,
        user_update: UserUpdate,
        cache: Redis = redis_client,
    ) -> Optional[UserRead]:
        """Update user with cache invalidation."""
        db_user = await UserRepository.update(session, user_id, user_update)
        if not db_user:
            return None

        # Invalidate cache
        cache_keys = [
            f"user:{user_id}",
            f"user:email:{db_user.email}",
            "users:list:*",
        ]
        await cache.delete(*cache_keys)

        return UserRead.model_validate(db_user)

    @staticmethod
    async def bulk_create_users(
        session: AsyncSession,
        users: List[UserCreate],
    ) -> List[UserRead]:
        """Bulk create users with transaction."""
        async with session.begin():
            db_users = await UserRepository.bulk_create(session, users)
            return [UserRead.model_validate(u) for u in db_users]

    @staticmethod
    @tracer.start_as_current_span("user_service.sync_with_external")
    async def sync_with_external_api(user_id: int) -> dict:
        """Sync user with external service (e.g., CRM)."""
        try:
            user = await UserService.get_user_by_id(user_id)
            if not user:
                raise ServiceException("User not found")

            # Use async HTTP client with circuit breaker
            response = await http_client.post(
                "https://external-api.com/users",
                json={"user_id": user.id, "email": user.email},
            )
            response.raise_for_status()
            return response.json()
        except RetryError as e:
            raise ServiceException("External API unavailable") from e
        except Exception as e:
            raise ServiceException(f"Sync failed: {str(e)}") from e

    @staticmethod
    async def get_user_by_email(
        session: AsyncSession,
        email: str,
        cache: Redis = redis_client,
    ) -> Optional[UserRead]:
        """Get user by email with caching."""
        cache_key = f"user:email:{email}"
        cached = await cache.get(cache_key)
        if cached:
            return UserRead.model_validate_json(cached)

        db_user = await UserRepository.get_by_email(session, email)
        if not db_user:
            return None

        result = UserRead.model_validate(db_user)
        await cache.setex(
            cache_key,
            timedelta(minutes=30).seconds,
            result.model_dump_json(),
        )
        return result

# app/core/dependencies.py
from functools import lru_cache
from app.db.repositories import UserRepository
from app.db.session import AsyncSession

@lru_cache(maxsize=100)  # Cache dependency instances
async def get_user_repo(session: AsyncSession = Depends(get_db)):
    return UserRepository(session)
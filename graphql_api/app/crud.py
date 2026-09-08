"""Async CRUD for the User model — real DB-backed resolvers."""
from typing import List, Optional

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def list_users(db: AsyncSession, first: int = 10, offset: int = 0) -> tuple[List[User], int]:
    total = (await db.execute(select(func.count(User.id)))).scalar_one()
    res = await db.execute(select(User).order_by(User.id).limit(first).offset(offset))
    return list(res.scalars().all()), total


async def create_user(db: AsyncSession, email: str, name: str, password: str, role: str = "user") -> User:
    user = User(email=email, name=name, password_hash=hash_password(password), role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

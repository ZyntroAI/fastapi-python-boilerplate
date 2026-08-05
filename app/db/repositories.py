# app/db/repositories.py
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

class ItemRepository:
    @staticmethod
    async def list_with_joins(session: AsyncSession, limit: int = 100) -> list[Item]:
        stmt = (
            select(Item)
            .options(joinedload(Item.author))  # Avoid N+1
            .order_by(Item.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().unique().all()  # .unique() prevents duplicates

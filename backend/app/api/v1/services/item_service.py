"""Business logic for the Item resource.

Services own the data access so routes stay thin. All functions take an
AsyncSession and raise domain errors from `app.core.exceptions`.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.models.item import Item
from app.api.v1.schemas.item import ItemCreate, ItemUpdate
from app.core.exceptions import ConflictError, NotFoundError


async def list_items(session: AsyncSession, *, offset: int = 0, limit: int = 100) -> list[Item]:
    stmt = select(Item).order_by(Item.id).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_item(session: AsyncSession, item_id: int) -> Item:
    item = await session.get(Item, item_id)
    if item is None:
        raise NotFoundError(f"Item {item_id} not found")
    return item


async def create_item(session: AsyncSession, data: ItemCreate) -> Item:
    existing = await session.execute(select(Item).where(Item.name == data.name))
    if existing.scalars().first() is not None:
        raise ConflictError(f"An item named '{data.name}' already exists")
    item = Item(**data.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def update_item(session: AsyncSession, item_id: int, data: ItemUpdate) -> Item:
    item = await get_item(session, item_id)
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        return item
    for field, value in changes.items():
        setattr(item, field, value)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def delete_item(session: AsyncSession, item_id: int) -> None:
    item = await get_item(session, item_id)
    await session.delete(item)
    await session.commit()

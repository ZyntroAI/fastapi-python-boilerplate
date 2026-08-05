from app.db.repositories import ItemRepository
from app.schemas.items import ItemCreate, ItemRead
from app.db.session import AsyncSession

class ItemService:
    @staticmethod
    async def create_item(session: AsyncSession, item: ItemCreate) -> ItemRead:
        db_item = await ItemRepository.create(session, item)
        return ItemRead.model_validate(db_item)

    @staticmethod
    async def get_item(session: AsyncSession, item_id: int) -> ItemRead | None:
        db_item = await ItemRepository.get(session, item_id)
        return ItemRead.model_validate(db_item) if db_item else None

# tests/test_services.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.items import ItemService

pytestmark = pytest.mark.anyio

async def test_service_create_and_list(db_session: AsyncSession):
    svc = ItemService(db_session)

    item = await svc.create_item(name="bar", owner_id=1)
    assert item.id is not None

    items = await svc.list_items(owner_id=1, limit=10, offset=0)
    assert len(items) == 1
    assert items[0].name == "bar"

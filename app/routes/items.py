from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.items import ItemCreate, ItemRead
from app.services.items import ItemService

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=ItemRead, status_code=201)
async def create_item(
    item: ItemCreate,
    session: AsyncSession = Depends(get_db),
):
    return await ItemService.create_item(session, item)

@router.get("/{item_id}", response_model=ItemRead)
async def read_item(
    item_id: int,
    session: AsyncSession = Depends(get_db),
):
    item = await ItemService.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

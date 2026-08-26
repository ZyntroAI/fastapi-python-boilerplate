from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.items import ItemCreate, ItemRead
from app.services.items import ItemService

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED, summary="Create a new item")
async def create_item(
    item: ItemCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new item in the database.
    - Validates input via `ItemCreate` schema.
    - Returns the created item as `ItemRead`.
    """
    return await ItemService.create_item(session, item)

@router.get("/{item_id}", response_model=ItemRead, summary="Get item by ID")
async def read_item(
    item_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single item by its ID.
    - Returns `404 Not Found` if the item does not exist.
    """
    item = await ItemService.get_item(session, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

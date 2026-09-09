"""Item CRUD routes demonstrating the full async data path.

- GET /items            list (public)
- POST /items           create (public in boilerplate; add CurrentUser to protect)
- GET/PATCH/DELETE      item by id

A protected example route (`GET /me`) shows JWT usage via `CurrentUser`.
"""
from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, DbSession
from app.api.v1.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.api.v1.services import item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemRead])
async def list_items(session: DbSession, offset: int = 0, limit: int = 100) -> list[ItemRead]:
    items = await item_service.list_items(session, offset=offset, limit=limit)
    return [ItemRead.model_validate(i) for i in items]


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate, session: DbSession) -> ItemRead:
    item = await item_service.create_item(session, data)
    return ItemRead.model_validate(item)


@router.get("/me", tags=["auth"])
async def whoami(user: CurrentUser) -> dict:
    """Protected route — requires a valid Bearer token.

    Defined before the parameterized /{item_id} routes so /items/me is not
    shadowed by the int-typed path param.
    """
    return {"username": user}


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, session: DbSession) -> ItemRead:
    item = await item_service.get_item(session, item_id)
    return ItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, data: ItemUpdate, session: DbSession) -> ItemRead:
    item = await item_service.update_item(session, item_id, data)
    return ItemRead.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, session: DbSession) -> Response:
    await item_service.delete_item(session, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

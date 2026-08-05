from fastapi import Depends
from app.core.cache import get_cached, set_cached

@router.get("/items/{item_id}")
async def read_item(
    item_id: int,
    session: AsyncSession = Depends(get_db),
    cache: redis.Redis = Depends(lambda: redis_client),
):
    cache_key = f"item:{item_id}"
    cached = await get_cached(cache_key)
    if cached:
        return json.loads(cached)

    item = await ItemService.get_item(session, item_id)
    if item:
        await set_cached(cache_key, item.model_dump_json(), ttl=30)
    return item

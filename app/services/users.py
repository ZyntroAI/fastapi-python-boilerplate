import asyncio
import uuid

# Simulated async “DB”
class UserRepo:
    async def create_user(self, email: str) -> dict:
        await asyncio.sleep(0.05)
        return {"id": str(uuid.uuid4()), "email": email}

    async def get_user(self, user_id: str) -> dict:
        await asyncio.sleep(0.05)
        return {"id": user_id, "email": f"user{user_id}@example.com"}

async def get_repo():
    # In real life: yield a DB session here (scoped per request)
    return UserRepo()

async def fanout_profile(user_id: str) -> dict:
    # Example concurrency: gather multiple IO calls
    async def fetch_a():
        await asyncio.sleep(0.08)
        return {"a": "value-a"}

    async def fetch_b():
        await asyncio.sleep(0.03)
        return {"b": "value-b"}

    async def fetch_c():
        await asyncio.sleep(0.06)
        return {"c": "value-c"}

    a, b, c = await asyncio.gather(fetch_a(), fetch_b(), fetch_c())
    return {"user_id": user_id, **a, **b, **c}

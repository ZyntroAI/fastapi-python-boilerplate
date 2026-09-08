"""GraphQL schema — Strawberry (Query / Mutation / Subscription)."""
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional

import strawberry

from app.auth import create_access_token


def _now() -> datetime:
    return datetime.now(timezone.utc)


@strawberry.type
class User:
    id: int
    email: str
    name: str
    role: str
    created_at: datetime


@strawberry.type
class PageInfo:
    has_next_page: bool
    end_cursor: Optional[str]


@strawberry.type
class UserEdge:
    node: User
    cursor: str


@strawberry.type
class UserConnection:
    edges: List[UserEdge]
    total_count: int
    page_info: PageInfo


@strawberry.type
class AuthPayload:
    access_token: str
    token_type: str = "bearer"
    user: User


def _require_user(context) -> dict:
    user = context.get("user")
    if not user:
        raise Exception("Not authenticated")
    return user


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: strawberry.Info) -> Optional[User]:
        user = _require_user(info.context)
        return User(id=int(user["sub"]), email=user.get("email", ""), name=user.get("name", ""),
                    role=user.get("role", "user"), created_at=_now())

    @strawberry.field
    async def users(self, info: strawberry.Info, first: int = 10, after: Optional[str] = None) -> UserConnection:
        _require_user(info.context)
        offset = int(after) if after and after.isdigit() else 0
        users = [User(id=i, email=f"user{i}@example.com", name=f"User {i}",
                      role="user", created_at=_now()) for i in range(offset + 1, offset + first + 1)]
        edges = [UserEdge(node=u, cursor=str(u.id)) for u in users]
        return UserConnection(edges=edges, total_count=100,
                              page_info=PageInfo(has_next_page=offset + first < 100,
                                                 end_cursor=str(users[-1].id) if users else None))


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, email: str, password: str) -> AuthPayload:
        # NOTE: replace with real user lookup + password verify (passlib/bcrypt).
        # Demo: any login returns a token for sub=1.
        token = create_access_token({"sub": "1", "email": email, "role": "admin"})
        user = User(id=1, email=email, name="Admin", role="admin", created_at=_now())
        return AuthPayload(access_token=token, user=user)

    @strawberry.mutation
    async def create_user(self, info: strawberry.Info, email: str, name: str, password: str) -> User:
        current = _require_user(info.context)
        if current.get("role") != "admin":
            raise Exception("Permission denied")
        return User(id=2, email=email, name=name, role="user", created_at=_now())


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def user_created(self) -> AsyncGenerator[User, None]:
        yield User(id=99, email="new@example.com", name="New User", role="user", created_at=_now())


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)

"""GraphQL schema — DB-backed Strawberry resolvers (Query / Mutation / Subscription)."""
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional

import strawberry

from app.auth import create_access_token
from app import crud


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


def _orm_to_gql(u) -> User:
    return User(id=u.id, email=u.email, name=u.name, role=u.role, created_at=u.created_at)


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: strawberry.Info) -> Optional[User]:
        user = _require_user(info.context)
        db = info.context["db"]
        row = await crud.get_user_by_id(db, int(user["sub"]))
        return _orm_to_gql(row) if row else None

    @strawberry.field
    async def users(self, info: strawberry.Info, first: int = 10,
                    after: Optional[str] = None) -> UserConnection:
        _require_user(info.context)
        db = info.context["db"]
        offset = int(after) if after and after.isdigit() else 0
        rows, total = await crud.list_users(db, first=first, offset=offset)
        edges = [UserEdge(node=_orm_to_gql(u), cursor=str(u.id)) for u in rows]
        last = rows[-1].id if rows else None
        return UserConnection(
            edges=edges, total_count=total,
            page_info=PageInfo(has_next_page=offset + len(rows) < total,
                               end_cursor=str(last) if last is not None else None))


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, info: strawberry.Info, email: str, password: str) -> AuthPayload:
        db = info.context["db"]
        row = await crud.get_user_by_email(db, email)
        if not row or not crud.verify_password(password, row.password_hash):
            raise Exception("Invalid email or password")
        token = create_access_token({"sub": str(row.id), "email": row.email, "role": row.role})
        return AuthPayload(access_token=token, user=_orm_to_gql(row))

    @strawberry.mutation
    async def create_user(self, info: strawberry.Info, email: str, name: str,
                          password: str) -> User:
        current = _require_user(info.context)
        if current.get("role") != "admin":
            raise Exception("Permission denied")
        db = info.context["db"]
        row = await crud.create_user(db, email=email, name=name, password=password)
        return _orm_to_gql(row)


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def user_created(self) -> AsyncGenerator[User, None]:
        yield User(id=99, email="new@example.com", name="New User", role="user", created_at=_now())


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)

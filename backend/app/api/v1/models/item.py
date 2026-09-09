"""SQLModel ORM models.

`Item` is the canonical example entity wired end-to-end (model -> schema ->
service -> route -> migration -> test) so the boilerplate demonstrates the full
data path. Add further models alongside it.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Item(SQLModel, table=True):
    """A persisted record with audit timestamps."""

    __tablename__ = "items"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    created_at: datetime = Field(
        default_factory=_utcnow, sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )

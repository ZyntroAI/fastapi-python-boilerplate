"""Database-backed user store (SQLAlchemy).

Replaces the JSON-file user records with a real table. On first init, users
that already exist in the legacy JSON store are imported, so no accounts are
lost in the migration.

Records are returned as plain dicts with the same shape the routers already
use — ``{"username", "hashed_password", "allowed_skills"}`` — so the API
surface and the per-user skill gating stay unchanged.
"""
import os

from sqlalchemy import JSON, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    """Declarative base for the user store."""


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    # NULL = unrestricted. A list restricts the user to those skills.
    allowed_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)


def _database_url() -> str:
    """DATABASE_URL if set, else SQLite next to the app data.

    Point this at Postgres in production, e.g.
    ``postgresql+psycopg://user:pass@host:5432/dbname``.
    """
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{settings.data_dir / 'users.db'}"


engine = create_engine(_database_url(), future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)


class UserStore:
    """Thin repository over the users table."""

    def init(self) -> None:
        """Create the table and import any legacy JSON-file users."""
        Base.metadata.create_all(engine)
        self._import_legacy_users()

    def _import_legacy_users(self) -> None:
        """One-time import from the old JSON store, if it has users."""
        from .db import db

        legacy = db.get("users", {}) or {}
        if not legacy:
            return
        with SessionLocal() as session:
            existing = {u for (u,) in session.execute(select(UserRow.username))}
            imported = 0
            for username, record in legacy.items():
                if username in existing:
                    continue
                session.add(
                    UserRow(
                        username=username,
                        hashed_password=record.get("hashed_password", ""),
                        allowed_skills=record.get("allowed_skills"),
                    )
                )
                imported += 1
            if imported:
                session.commit()

    def get(self, username: str) -> dict | None:
        with SessionLocal() as session:
            row = session.execute(
                select(UserRow).where(UserRow.username == username)
            ).scalar_one_or_none()
            return self._to_dict(row)

    def exists(self, username: str) -> bool:
        with SessionLocal() as session:
            found = session.execute(
                select(UserRow.id).where(UserRow.username == username)
            ).first()
            return found is not None

    def count(self) -> int:
        with SessionLocal() as session:
            return session.execute(select(func.count(UserRow.id))).scalar_one()

    def create(
        self, username: str, hashed_password: str, allowed_skills: list | None = None
    ) -> dict:
        with SessionLocal() as session:
            row = UserRow(
                username=username,
                hashed_password=hashed_password,
                allowed_skills=allowed_skills,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_dict(row)

    def set_allowed_skills(self, username: str, allowed_skills: list | None) -> bool:
        with SessionLocal() as session:
            row = session.execute(
                select(UserRow).where(UserRow.username == username)
            ).scalar_one_or_none()
            if row is None:
                return False
            row.allowed_skills = allowed_skills
            session.commit()
            return True

    def allowed_skills(self, username: str) -> set | None:
        """None = unrestricted; a set restricts the user to those skills."""
        record = self.get(username)
        if record is None:
            return None
        allowed = record.get("allowed_skills")
        return None if allowed is None else set(allowed)

    @staticmethod
    def _to_dict(row: UserRow | None) -> dict | None:
        if row is None:
            return None
        return {
            "username": row.username,
            "hashed_password": row.hashed_password,
            "allowed_skills": row.allowed_skills,
        }


user_store = UserStore()

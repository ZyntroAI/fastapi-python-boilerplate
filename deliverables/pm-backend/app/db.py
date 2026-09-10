"""Database layer with OPT-IN encryption at rest.

The app does NOT hard-depend on an encryption library. When
``ENCRYPT_AT_REST=true`` we use a SQLAlchemy TypeDecorator to transparently
encrypt string fields with Fernet before they hit the database and decrypt
them on read. When it is false (the default), the same fields are stored as
plain text and the ``cryptography`` package is never imported.
"""
from __future__ import annotations

import base64
import hashlib
import os
from typing import Any

from sqlalchemy import Column, String, create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import TypeDecorator

from .config import get_settings


def _build_fernet(secret: str, key: str) -> Any:
    """Construct a Fernet instance from an explicit key or a derived secret."""
    from cryptography.fernet import Fernet  # lazy import

    if key:
        return Fernet(key.encode("utf-8"))
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


class EncryptedString(TypeDecorator):
    """Transparent at-rest encryption for string columns (opt-in)."""

    impl = String
    cache_ok = True

    def __init__(self, *args, fernet=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fernet = fernet

    def process_bind_param(self, value, dialect):
        if value is None or self.fernet is None:
            return value
        return self.fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def process_result_value(self, value, dialect):
        if value is None or self.fernet is None:
            return value
        return self.fernet.decrypt(value.encode("utf-8")).decode("utf-8")


def _string_column(fernet: Any | None) -> Column:
    """Plain or encrypted string column depending on the setting."""
    if fernet is not None:
        return Column(EncryptedString(fernet=fernet))
    return Column(String)


settings = get_settings()

_fernet: Any | None = None
if settings.encrypt_at_rest:
    _fernet = _build_fernet(settings.encryption_secret, settings.encryption_key)

engine = create_engine(
    settings.database_url,
    connect_args=(
        {"check_same_thread": False}
        if settings.database_url.startswith("sqlite")
        else {}
    ),
)

if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class ProgramRecord(Base):
    """A row in the program registry. ``note`` is the encrypted field."""

    __tablename__ = "programs"

    id = Column(String, primary_key=True, default=lambda: os.urandom(8).hex())
    name = Column(String, nullable=False)
    owner = Column(String, default="")
    status = Column(String, default="planned")
    note = _string_column(_fernet)  # encrypted only when ENCRYPT_AT_REST=true


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

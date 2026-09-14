"""Program repository: read/write ProgramRecord rows.

These helpers exist so the API can create and fetch programs, transparently
exercising the optional at-rest encryption on the ``note`` column. The layer
is identical whether or not ENCRYPT_AT_REST is enabled — the difference lives
entirely in the SQLAlchemy column type selected in ``db``.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from .db import ProgramRecord


def create_program(
    db: Session,
    name: str,
    owner: str = "",
    status: str = "planned",
    note: str = "",
) -> ProgramRecord:
    record = ProgramRecord(name=name, owner=owner, status=status, note=note)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_program(db: Session, program_id: str) -> ProgramRecord | None:
    return db.get(ProgramRecord, program_id)


def list_programs(db: Session) -> list[ProgramRecord]:
    return db.query(ProgramRecord).order_by(ProgramRecord.name).all()

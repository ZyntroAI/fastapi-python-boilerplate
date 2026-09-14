"""Program Management CSV template generation.

Provides a canonical CSV structure for managing programs (portfolios of
projects) and tools to (a) render a blank template, (b) fill a template from
a list of program rows, and (c) parse uploaded CSV into structured rows.

Column model (a complete program-management sheet):
    program_id, name, owner, status, start_date, end_date,
    budget, spent, risk, health, milestone, notes
"""
from __future__ import annotations

import csv
import io
from typing import Any, Sequence

from pydantic import BaseModel, Field, field_validator

CSV_COLUMNS = [
    "program_id",
    "name",
    "owner",
    "status",
    "start_date",
    "end_date",
    "budget",
    "spent",
    "risk",
    "health",
    "milestone",
    "notes",
]

VALID_STATUS = {"planned", "active", "on_hold", "completed", "cancelled"}
VALID_HEALTH = {"green", "amber", "red"}


class ProgramRow(BaseModel):
    """A single row in the program management sheet."""

    program_id: str = Field(default="", description="Unique program id")
    name: str = Field(..., min_length=1, description="Program name")
    owner: str = Field(default="", description="Owning individual/team")
    status: str = Field(default="planned")
    start_date: str = Field(default="")
    end_date: str = Field(default="")
    budget: float | None = Field(default=None, ge=0)
    spent: float | None = Field(default=None, ge=0)
    risk: str = Field(default="")
    health: str = Field(default="green")
    milestone: str = Field(default="")
    notes: str = Field(default="")

    @field_validator("status")
    @classmethod
    def _status(cls, v: str) -> str:
        v = v.strip().lower()
        if v and v not in VALID_STATUS:
            raise ValueError(f"status must be one of {sorted(VALID_STATUS)}")
        return v

    @field_validator("health")
    @classmethod
    def _health(cls, v: str) -> str:
        v = v.strip().lower()
        if v and v not in VALID_HEALTH:
            raise ValueError(f"health must be one of {sorted(VALID_HEALTH)}")
        return v


def template_csv() -> str:
    """Return a blank, ready-to-fill CSV template (headers + one example row
    commented out is not possible in CSV, so we include one fully-formed
    example row the caller can delete)."""
    return rows_to_csv([ProgramRow(name="Example Program", status="active")])


def rows_to_csv(rows: Sequence[ProgramRow | dict[str, Any]]) -> str:
    """Serialize program rows into CSV text (header row included)."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for row in rows:
        p = row if isinstance(row, ProgramRow) else ProgramRow(**row)
        writer.writerow(
            [
                p.program_id,
                p.name,
                p.owner,
                p.status,
                p.start_date,
                p.end_date,
                "" if p.budget is None else f"{p.budget:g}",
                "" if p.spent is None else f"{p.spent:g}",
                p.risk,
                p.health,
                p.milestone,
                p.notes,
            ]
        )
    return out.getvalue()


def parse_csv(text: str) -> list[ProgramRow]:
    """Parse CSV text into validated ProgramRow objects."""
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV is empty or has no header row")
    missing = [c for c in CSV_COLUMNS if c not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    rows: list[ProgramRow] = []
    for lineno, raw in enumerate(reader, start=2):
        if not any((raw.get(c) or "").strip() for c in CSV_COLUMNS):
            continue  # skip fully-blank lines
        # CSV cells for optional numeric fields arrive as "" — map to None.
        clean = dict(raw)
        for num_field in ("budget", "spent"):
            if (clean.get(num_field) or "").strip() == "":
                clean[num_field] = None
        try:
            rows.append(ProgramRow(**clean))
        except Exception as exc:  # pydantic ValidationError
            raise ValueError(f"Row {lineno}: {exc}") from exc
    return rows

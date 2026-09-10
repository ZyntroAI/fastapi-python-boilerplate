"""Program Management - CSV generation."""
import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/programs", tags=["programs"])


class Program(BaseModel):
    id: str
    name: str
    status: str = "planned"
    owner: str = ""
    start: str = ""
    end: str = ""
    budget: float = 0.0
    progress: int = 0


@router.get("/sample")
def sample_programs():
    return [
        Program(id="P1", name="Website launch", status="active", owner="Ava",
                start="2026-09-01", end="2026-10-15", budget=12000, progress=30),
        Program(id="P2", name="API v2", status="planned", owner="Ben",
                start="2026-10-01", end="2026-12-01", budget=30000, progress=0),
    ]


@router.post("/export")
def export_csv(programs: list[Program]):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "name", "status", "owner", "start", "end", "budget", "progress"])
    for p in programs:
        writer.writerow([p.id, p.name, p.status, p.owner, p.start, p.end, p.budget, p.progress])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=programs.csv"})

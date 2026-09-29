"""
PackageMonitor API — Trigger Scans • View Reports
Mount at: /api/v1/package
"""

from datetime import datetime
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
import json, subprocess

router = APIRouter(prefix="/api/v1/package", tags=["Package Monitor"])
LATEST_REPORT = Path(__file__).parent.parent.parent.parent / "reports" / "package-monitor" / "latest.json"

# ─── Schemas ──────────────────────────────────
class IssueItem(BaseModel):
    severity: str
    category: str
    package: str
    message: str
    fix: str
    timestamp: str

class PackageReport(BaseModel):
    scanned_at: str
    status: str
    total_issues: int
    critical_count: int
    high_count: int
    issues: list[IssueItem]

# ─── Endpoints ────────────────────────────────
@router.get("/latest", response_model=PackageReport, summary="Latest scan result")
async def get_latest():
    if not LATEST_REPORT.exists():
        return PackageReport(
            scanned_at=datetime.utcnow().isoformat(),
            status="unknown",
            total_issues=0,
            critical_count=0,
            high_count=0,
            issues=[],
        )
    return json.loads(LATEST_REPORT.read_text(encoding="utf-8"))

@router.post("/scan", summary="Run scan now")
async def trigger_scan():
    result = subprocess.run(
        ["python", str(Path(__file__).parent / "package_monitor.py")],
        capture_output=True, text=True
    )
    return {
        "exit_code": result.returncode,
        "status": "FAIL" if result.returncode else "PASS",
        "output": result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout,
    }

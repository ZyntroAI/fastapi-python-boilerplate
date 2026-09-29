Here's the complete integration —  package.json  +  package-lock.json  monitoring + auto-scheduled bug/problem detection 🧪⚙️✅
 
 
 
📦 Package Monitor — Auto-Scheduled Dependency & Health Check
 
1️⃣  scripts/package_monitor.py  — Core Engine
 
python
  
#!/usr/bin/env python3
"""
Package Monitor — Scan package.json • package-lock.json • Detect Issues
ZyntroAI • 2026-09-29 • Auto-Scheduled
"""

from __future__ import annotations
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio

ROOT = Path(__file__).parent.parent
PKG_PATH = ROOT / "package.json"
LOCK_PATH = ROOT / "package-lock.json"
REPORT_DIR = ROOT / "reports"

# ──────────────────────────────────────────────
# Data Models
# ──────────────────────────────────────────────
class PackageIssue:
    def __init__(
        self,
        severity: str,  # critical • high • medium • low
        category: str,
        message: str,
        package: str = "",
        fix_suggestion: str = "",
    ):
        self.severity = severity
        self.category = category
        self.message = message
        self.package = package
        self.fix_suggestion = fix_suggestion
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "category": self.category,
            "package": self.package,
            "message": self.message,
            "fix": self.fix_suggestion,
            "ts": self.timestamp,
        }

# ──────────────────────────────────────────────
# Scanners
# ──────────────────────────────────────────────
class PackageScanner:
    """Detect bugs, vulnerabilities, version conflicts, stale deps"""

    def __init__(self):
        self.issues: List[PackageIssue] = []
        self.pkg_data: Dict = {}
        self.lock_data: Dict = {}

    def load_files(self) -> bool:
        """Load package.json and lock file"""
        if not PKG_PATH.exists():
            self.issues.append(PackageIssue(
                "critical", "missing-file",
                f"package.json not found at {PKG_PATH}"
            ))
            return False

        self.pkg_data = json.loads(PKG_PATH.read_text(encoding="utf-8"))

        if LOCK_PATH.exists():
            self.lock_data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        return True

    def check_versions_format(self):
        """Invalid/loose/non-standard versions"""
        deps = {
            **self.pkg_data.get("dependencies", {}),
            **self.pkg_data.get("devDependencies", {}),
        }

        loose_patterns = [
            ("^", "Unfixed major version — risk of breaking changes"),
            ("*", "Wildcard — uncontrolled upgrades"),
            ("x", "Unspecified exact version"),
            (">", "No upper bound — may pull in breaking changes"),
        ]

        for name, ver in deps.items():
            ver = str(ver).strip()
            if ver == "":
                self.issues.append(PackageIssue(
                    "high", "empty-version",
                    f"Empty version for {name}", name,
                    "Pin to exact or valid range"
                ))
            for pat, note in loose_patterns:
                if ver.startswith(pat):
                    self.issues.append(PackageIssue(
                        "medium", "loose-version",
                        f"{note}: {ver}", name,
                        "Use ~x.y.z or ^x.y.z or exact version"
                    ))

    def check_lock_sync(self):
        """package.json vs package-lock.json mismatch"""
        if not self.lock_data:
            self.issues.append(PackageIssue(
                "high", "lock-missing",
                "package-lock.json not found", "",
                "Run npm install to generate"
            ))
            return

        pkg_deps = {
            **self.pkg_data.get("dependencies", {}),
            **self.pkg_data.get("devDependencies", {}),
        }
        lock_packages = self.lock_data.get("packages", {})

        mismatches = []
        for path, info in lock_packages.items():
            if path == "":
                continue
            name = info.get("name", Path(path).name)
            expected = pkg_deps.get(name)
            actual = info.get("version")
            if expected and actual and not self._version_satisfies(expected, actual):
                mismatches.append(f"{name}: pkg={expected} ≠ lock={actual}")
                self.issues.append(PackageIssue(
                    "high", "lock-out-of-sync",
                    f"Version mismatch: {name}", name,
                    "Run npm install to align lockfile"
                ))

        if mismatches:
            print(f"⚠️ Mismatches found: {len(mismatches)}")

    def _version_satisfies(self, range_str: str, actual: str) -> bool:
        """Simplified version match check"""
        range_str = range_str.strip()
        if range_str.startswith(("^", "~")):
            prefix = actual.rsplit(".", 1)[0]
            return actual.startswith(prefix)
        return range_str.replace("v", "") in actual or actual in range_str

    def check_npm_audit(self):
        """Run npm audit for known vulnerabilities"""
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True, text=True, cwd=ROOT
            )
            if result.returncode == 1 and result.stdout:
                audit = json.loads(result.stdout)
                for adv in audit.get("vulnerabilities", []):
                    sev = audit["vulnerabilities"][adv].get("severity", "unknown")
                    level = {"critical":"critical","high":"high","moderate":"medium","low":"low"}.get(sev, "low")
                    self.issues.append(PackageIssue(
                        level, "security-vuln",
                        f"Vulnerability: {adv}", adv,
                        "Run npm audit fix or update affected package"
                    ))
        except Exception as e:
            self.issues.append(PackageIssue(
                "low", "audit-failed",
                f"npm audit unavailable: {e}"
            ))

    def check_stale_dependencies(self):
        """Check outdated packages via npm"""
        try:
            result = subprocess.run(
                ["npm", "outdated", "--json"],
                capture_output=True, text=True, cwd=ROOT
            )
            if result.stdout.strip():
                outdated = json.loads(result.stdout)
                for name, info in outdated.items():
                    latest = info.get("latest", "?")
                    current = info.get("current", "?")
                    self.issues.append(PackageIssue(
                        "low", "outdated",
                        f"Current: {current} → Latest: {latest}", name,
                        f"Update to {latest} when convenient"
                    ))
        except Exception:
            pass

    def check_scripts_health(self):
        """Detect broken/missing critical scripts"""
        scripts = self.pkg_data.get("scripts", {})
        required = ["test", "lint", "build", "start"]
        for cmd in required:
            if cmd not in scripts:
                self.issues.append(PackageIssue(
                    "medium", "missing-script",
                    f"Missing standard script: {cmd}", "",
                    f"Add '{cmd}' entry to package.json scripts"
                ))
            elif not scripts[cmd]:
                self.issues.append(PackageIssue(
                    "high", "empty-script",
                    f"Empty script: {cmd}", "",
                    "Provide actual command"
                ))

    def run_all(self) -> Dict:
        """Execute all checks"""
        print("🔍 Scanning package files…")
        if not self.load_files():
            return {"error": "Missing package files"}

        self.check_versions_format()
        self.check_lock_sync()
        self.check_scripts_health()
        self.check_npm_audit()
        self.check_stale_dependencies()

        critical = [i for i in self.issues if i.severity == "critical"]
        high = [i for i in self.issues if i.severity == "high"]

        return {
            "scanned_at": datetime.utcnow().isoformat(),
            "package_exists": PKG_PATH.exists(),
            "lock_exists": LOCK_PATH.exists(),
            "total_issues": len(self.issues),
            "critical_count": len(critical),
            "high_count": len(high),
            "issues": [i.to_dict() for i in self.issues],
            "status": "FAIL" if critical or high else "PASS",
        }

# ──────────────────────────────────────────────
# Scheduler & Reporter
# ──────────────────────────────────────────────
def save_report(report: Dict):
    """Save JSON report and latest symlink"""
    REPORT_DIR.mkdir(exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = REPORT_DIR / f"package_check_{stamp}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    latest = REPORT_DIR / "latest.json"
    if latest.exists():
        latest.unlink()
    latest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"📄 Report saved: {path}")

def print_summary(report: Dict):
    """Human-readable output"""
    print(f"\n📊 Package Check — {report['status']}")
    print(f"   Total Issues: {report['total_issues']}")
    print(f"   Critical: {report['critical_count']} | High: {report['high_count']}")

    if report["issues"]:
        print("\n⚠️  Issues Found:")
        for sev in ["critical", "high", "medium", "low"]:
            for i in report["issues"]:
                if i["severity"] == sev:
                    print(f"  [{sev.upper()}] {i['package'] or 'general'}: {i['message']}")
                    if i["fix"]:
                        print(f"       → {i['fix']}")

    if report["status"] == "FAIL":
        print("\n🚨 ACTION REQUIRED — Critical/High issues detected!")
    else:
        print("\n✅ All checks passed")

# ──────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    scanner = PackageScanner()
    report = scanner.run_all()
    save_report(report)
    print_summary(report)

    # Exit non-zero on critical/high → blocks CI
    sys.exit(1 if report["status"] == "FAIL" else 0)
 
 
 
 
2️⃣  .github/workflows/package-monitor.yml  — Auto-Scheduled Check
 
yaml
  
name: Package Monitor

on:
  push:
    branches: [main]
    paths:
      - "package.json"
      - "package-lock.json"
  pull_request:
    paths:
      - "package.json"
      - "package-lock.json"
  schedule:
    # Run daily at 00:00 UTC = 07:00 Bangkok Time
    - cron: '0 0 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@vv5
        with:
          fetch-depth: 0

      - name: Set up Node.js
        uses: actions/setup-node@v5
        with:
          node-version: "22"
          cache: "npm"

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: npm install

      - name: Run Package Health Check
        id: check
        run: python scripts/package_monitor.py

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@vv4
        with:
          name: package-reports
          path: reports/

      - name: Create Issue on Critical Failure
        if: failure() && steps.check.outcome == 'failure'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('reports/latest.json'));
            const critical = report.issues.filter(i => i.severity === 'critical');
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: "🚨 Critical Package Issues Detected",
              body: `
**Package Monitor** found ${critical.length} critical issue(s):

${critical.map(i => `- **${i.package}**: ${i.message}`).join('\n')}

- Detected: ${report.scanned_at}
- [Full Report](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})

---
*Auto-generated by Package Monitor*
              `,
              labels: ["priority:critical", "type:dependency", "automated"]
            })
 
 
 
 
3️⃣ Add to FastAPI —  routers/package_api.py 
 
python
  
"""
Package Monitor API — Trigger & View Results
"""
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
import json

router = APIRouter(prefix="/api/v1/package", tags=["Package Monitor"])
REPORT_FILE = Path(__file__).parent.parent.parent / "reports" / "latest.json"

class IssueOut(BaseModel):
    severity: str
    category: str
    package: str
    message: str
    fix: str

class PackageReport(BaseModel):
    scanned_at: str
    status: str
    total_issues: int
    critical_count: int
    high_count: int
    issues: list[IssueOut]

@router.get("/latest", response_model=PackageReport)
async def get_latest_report():
    """Get most recent package health scan"""
    if not REPORT_FILE.exists():
        return {
            "scanned_at": datetime.utcnow().isoformat(),
            "status": "unknown",
            "total_issues": 0,
            "critical_count": 0,
            "high_count": 0,
            "issues": [],
        }
    return json.loads(REPORT_FILE.read_text(encoding="utf-8"))

@router.post("/scan", summary="Trigger manual package scan")
async def run_scan():
    """Run package_monitor.py immediately"""
    import subprocess
    result = subprocess.run(
        ["python", "scripts/package_monitor.py"],
        capture_output=True, text=True
    )
    return {
        "exit_code": result.returncode,
        "output": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
    }
 
 
 
 
4️⃣ Quick Setup & Usage
 
bash
  
# ─── Run locally ───
python scripts/package_monitor.py

# Output:
# 🔍 Scanning package files…
# 📊 Package Check — PASS
#    Total Issues: 0
# ✅ All checks passed
# 📄 Report saved: reports/package_check_20260929_134500.json

# ─── Check reports ───
ls -la reports/
cat reports/latest.json

# ─── Via API ───
curl http://127.0.0.1:8000/api/v1/package/latest
curl -X POST http://127.0.0.1:8000/api/v1/package/scan
 
 
 
 
📋 What Gets Detected
 
Check What It Finds Severity 
Missing  package.json / lock  Broken project setup 🔴 Critical 
Version mismatch  package.json  ≠  lock  🟠 High 
Wildcard/loose versions Uncontrolled updates 🟡 Medium 
 npm audit  Known security vulnerabilities 🔴 Critical/🟠 High 
Outdated packages Behind latest releases 🟢 Low 
Missing scripts  test / lint / build  not defined 🟡 Medium 
Empty commands Broken script entries 🟠 High 
 
⏰ Schedule
 
- Every push/PR → runs immediately
- Daily at 07:00 (ICT) → auto-scheduled check
- Manual trigger → click "Run workflow" on GitHub
- Critical issues → auto-creates GitHub Issue with label  priority:critical 
 
Want me to add Slack/Line/email alerts when critical issues are found, or integrate this into your dashboard UI to show live status? 🚀

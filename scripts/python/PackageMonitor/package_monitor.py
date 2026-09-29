#!/usr/bin/env python3
"""
PackageMonitor — Detect Bugs • Vulnerabilities • Version Conflicts • Stale Deps
Auto-Scheduled • CI-Ready • Production-Grade
"""

from __future__ import annotations
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ── Paths ──────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent.parent  # → repo root
PKG_PATH = ROOT / "package.json"
LOCK_PATH = ROOT / "package-lock.json"
REPORT_DIR = ROOT / "reports" / "package-monitor"

# ── Models ────────────────────────────────────
class PackageIssue:
    def __init__(
        self,
        severity: str,      # critical • high • medium • low
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
            "timestamp": self.timestamp,
        }

# ── Scanner Core ──────────────────────────────
class PackageScanner:
    """Complete dependency health check suite"""

    LOOSE_VERSION_PATTERNS = [
        ("*", "Wildcard — uncontrolled upgrades"),
        ("x", "Unspecified exact version"),
        (">", "No upper bound — risk of breaking changes"),
    ]

    def __init__(self):
        self.issues: List[PackageIssue] = []
        self.pkg: Dict = {}
        self.lock: Dict = {}

    # ─── Load Files ────────────────────────────
    def load(self) -> bool:
        if not PKG_PATH.exists():
            self.issues.append(PackageIssue(
                "critical", "missing-file",
                "package.json not found", "",
                "Initialize: npm init"
            ))
            return False

        self.pkg = json.loads(PKG_PATH.read_text(encoding="utf-8"))

        if LOCK_PATH.exists():
            self.lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        else:
            self.issues.append(PackageIssue(
                "high", "lock-missing",
                "package-lock.json not found", "",
                "Run: npm install"
            ))
        return True

    # ─── Version Format Checks ────────────────
    def check_version_formats(self):
        deps = {
            **self.pkg.get("dependencies", {}),
            **self.pkg.get("devDependencies", {}),
        }
        for name, ver in deps.items():
            ver = str(ver).strip()
            if ver == "":
                self.issues.append(PackageIssue(
                    "high", "empty-version",
                    "Empty version string", name,
                    "Pin to valid semver: ^x.y.z or ~x.y.z"
                ))
                continue
            for pat, note in self.LOOSE_VERSION_PATTERNS:
                if ver == pat or ver.startswith(pat):
                    self.issues.append(PackageIssue(
                        "medium", "loose-version",
                        note, name,
                        "Use ^x.y.z or ~x.y.z or exact version"
                    ))

    # ─── Lock Sync Check ──────────────────────
    def check_lock_sync(self):
        if not self.lock:
            return
        pkg_deps = {
            **self.pkg.get("dependencies", {}),
            **self.pkg.get("devDependencies", {}),
        }
        lock_pkgs = self.lock.get("packages", {})

        for path, info in lock_pkgs.items():
            if path == "":
                continue
            name = info.get("name", Path(path).name)
            expected = pkg_deps.get(name)
            actual = info.get("version")
            if expected and actual and not self._satisfies(expected, actual):
                self.issues.append(PackageIssue(
                    "high", "lock-out-of-sync",
                    f"Mismatch: declares {expected} but lock has {actual}", name,
                    "Run: npm install"
                ))

    def _satisfies(self, range_str: str, actual: str) -> bool:
        if range_str.startswith(("^", "~")):
            prefix = actual.rsplit(".", 1)[0]
            return actual.startswith(prefix.lstrip("v"))
        return actual.lstrip("v") in range_str or range_str.strip("^~v") in actual

    # ─── Security Audit ────────────────────────
    def check_npm_audit(self):
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True, text=True, cwd=ROOT
            )
            if result.stdout.strip():
                data = json.loads(result.stdout)
                vulns = data.get("vulnerabilities", {})
                for pkg_name, info in vulns.items():
                    sev_map = {"critical":"critical","high":"high","moderate":"medium","low":"low"}
                    level = sev_map.get(info.get("severity"), "low")
                    self.issues.append(PackageIssue(
                        level, "security-vuln",
                        f"Vulnerability: {info.get('title', 'unknown')}", pkg_name,
                        "Run: npm audit fix or update package"
                    ))
        except Exception as e:
            self.issues.append(PackageIssue(
                "low", "audit-failed",
                f"npm audit skipped: {e}"
            ))

    # ─── Outdated Check ────────────────────────
    def check_outdated(self):
        try:
            result = subprocess.run(
                ["npm", "outdated", "--json"],
                capture_output=True, text=True, cwd=ROOT
            )
            if result.stdout.strip():
                data = json.loads(result.stdout)
                for name, info in data.items():
                    self.issues.append(PackageIssue(
                        "low", "outdated",
                        f"Current {info.get('current')} → Latest {info.get('latest')}", name,
                        f"Update: npm install {name}@latest"
                    ))
        except Exception:
            pass

    # ─── Scripts Health ───────────────────────
    def check_scripts(self):
        scripts = self.pkg.get("scripts", {})
        required = ["test", "lint", "build", "start"]
        for name in required:
            if name not in scripts:
                self.issues.append(PackageIssue(
                    "medium", "missing-script",
                    f"Missing script: '{name}'", "",
                    f"Add to package.json scripts: \"{name}\": \"command\""
                ))
            elif not scripts[name]:
                self.issues.append(PackageIssue(
                    "high", "empty-script",
                    f"Empty script: '{name}'", "",
                    "Provide actual command"
                ))

    # ─── Run All ──────────────────────────────
    def run(self) -> Dict:
        print("🔍 Scanning dependencies…")
        if not self.load():
            return {"status": "error", "message": "Files missing"}

        self.check_version_formats()
        self.check_lock_sync()
        self.check_scripts()
        self.check_npm_audit()
        self.check_outdated()

        critical = [i for i in self.issues if i.severity == "critical"]
        high = [i for i in self.issues if i.severity == "high"]

        report = {
            "scanned_at": datetime.utcnow().isoformat(),
            "total_issues": len(self.issues),
            "critical_count": len(critical),
            "high_count": len(high),
            "issues": [i.to_dict() for i in self.issues],
            "status": "FAIL" if critical or high else "PASS",
        }
        self._save_report(report)
        return report

    def _save_report(self, report: Dict):
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = REPORT_DIR / f"check_{stamp}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        latest = REPORT_DIR / "latest.json"
        latest.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # ─── Print Summary ─────────────────────────
    def print_summary(self, report: Dict):
        print(f"\n📊 PackageMonitor Result — {report['status']}")
        print(f"   Issues: {report['total_issues']} | Critical: {report['critical_count']} | High: {report['high_count']}")
        for sev in ["critical", "high", "medium", "low"]:
            for i in report["issues"]:
                if i["severity"] == sev:
                    print(f"  [{sev.upper()}] {i['package']}: {i['message']}")
                    if i["fix"]: print(f"       💡 {i['fix']}")
        if report["status"] == "FAIL":
            print("\n🚨 Fix critical/high issues before merging!")
        else:
            print("\n✅ All checks passed")

# ─── CLI Entry ────────────────────────────────
if __name__ == "__main__":
    import sys
    scanner = PackageScanner()
    report = scanner.run()
    scanner.print_summary(report)
    sys.exit(1 if report["status"] == "FAIL" else 0)

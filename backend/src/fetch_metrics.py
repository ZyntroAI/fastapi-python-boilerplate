#!/usr/bin/env python3
"""
Fetch ALL GitHub Copilot Organization Metrics
API Docs: https://docs.github.com/rest/copilot
Endpoints: Metrics | Seats | Usage Summary | Languages | Editors
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
import requests

# ─── CONFIGURATION ────────────────────────────────────────────────
GITHUB_API_BASE = "https://api.github.com"
API_VERSION = "2022-11-28"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = os.getenv("GITHUB_ORG_NAME", "ZyntroAI")

OUTPUT_DIR = Path(__file__).parent.parent / "copilot-metrics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TIMESTAMP = datetime.utcnow().strftime("%Y%m%d-%H%M%S-UTC")

# ─── HELPERS ─────────────────────────────────────────────────────
def get_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }

def save_json(data, name):
    path = OUTPUT_DIR / f"{name}-{TIMESTAMP}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 JSON → {path.name}")
    return path

def save_csv(rows, name, fieldnames):
    path = OUTPUT_DIR / f"{name}-{TIMESTAMP}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"📄 CSV → {path.name}")
    return path

def api_get(endpoint, desc):
    """Generic API GET with unified error handling"""
    url = f"{GITHUB_API_BASE}/{endpoint}"
    print(f"\n📡 {desc}...")
    resp = requests.get(url, headers=get_headers(), timeout=30)

    if resp.status_code == 403:
        print("❌ 403 Forbidden — check token scopes: manage_billing:copilot or read:org")
        return None
    if resp.status_code == 404:
        print("❌ 404 Not Found — verify org name & Copilot Business/Enterprise plan")
        return None
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}: {resp.text[:300]}")
        return None

    data = resp.json()
    print(f"✅ OK", end="")
    return data

# ─── ENDPOINT: DETAILED METRICS (daily breakdown) ────────────────
def fetch_detailed_metrics():
    """
    /orgs/{org}/copilot/metrics
    → Daily stats: users, accept rates, languages, editors, models
    """
    data = api_get(f"orgs/{ORG_NAME}/copilot/metrics", "Detailed Daily Metrics")
    if not data:
        return None
    print(f" — {len(data)} day(s) retrieved")
    save_json(data, "copilot-detailed")
    return data

# ─── ENDPOINT: SEAT ASSIGNMENT ──────────────────────────────────
def fetch_seats():
    """
    /orgs/{org}/copilot/seats
    → Who has Copilot, when assigned, last activity, plan type
    """
    data = api_get(f"orgs/{ORG_NAME}/copilot/seats?per_page=100", "Seat Assignments")
    if not data:
        return None
    total = data.get("total_seats", "?")
    seats = data.get("seats", [])
    print(f" — {total} total seats, {len(seats)} on page 1")
    save_json(data, "copilot-seats")

    # CSV export for easy auditing
    rows = []
    for s in seats:
        user = s.get("assignee", {})
        rows.append({
            "login": user.get("login"),
            "email": user.get("email", "private"),
            "status": s.get("status"),
            "assigned_at": s.get("assigned_at"),
            "last_activity_at": s.get("last_activity_at"),
            "last_activity_editor": s.get("last_activity_editor"),
            "plan_type": s.get("plan_type"),
        })
    if rows:
        save_csv(rows, "copilot-seats-audit", list(rows[0].keys()))
    return data

# ─── ENDPOINT: USAGE SUMMARY ─────────────────────────────────────
def fetch_usage_summary():
    """
    /orgs/{org}/copilot/usage
    → Aggregated usage over time period (default: last 28 days)
    """
    data = api_get(f"orgs/{ORG_NAME}/copilot/usage", "28-Day Usage Summary")
    if not data:
        return None
    print(f" — {len(data)} days of usage")
    save_json(data, "copilot-usage")

    # Quick summary
    total_suggested = sum(d.get("total_code_suggestions", 0) for d in data)
    total_accepted = sum(d.get("total_code_acceptances", 0) for d in data)
    rate = round(total_accepted/total_suggested*100, 1) if total_suggested else 0
    print(f"   Total suggestions: {total_suggested} | accepted: {total_accepted} | rate: {rate}%")
    return data

# ─── AGGREGATED SUMMARY REPORT ───────────────────────────────────
def build_summary_report(metrics, usage, seats):
    """Build a single consolidated overview file"""
    latest = metrics[0] if isinstance(metrics, list) and metrics else {}
    report = {
        "generated_utc": datetime.utcnow().isoformat(),
        "organization": ORG_NAME,
        "period_days": len(metrics) if isinstance(metrics, list) else 0,
        "latest_date": latest.get("date"),
        "total_active_users": latest.get("total_active_users"),
        "total_engaged_users": latest.get("total_engaged_users"),
        "total_seats": seats.get("total_seats") if seats else None,
        "suggestions_28d": sum(d.get("total_code_suggestions", 0) for d in (usage or [])),
        "acceptances_28d": sum(d.get("total_code_acceptances", 0) for d in (usage or [])),
    }
    save_json(report, "copilot-summary")
    print("\n📋 Consolidated Summary:")
    for k,v in report.items():
        print(f"   {k}: {v}")
    return report

# ─── MAIN ────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("❌ Missing GITHUB_TOKEN environment variable!")
        raise SystemExit(1)

    print(f"=== 🚀 Fetching Copilot Data for {ORG_NAME} ===")

    metrics = fetch_detailed_metrics()
    usage = fetch_usage_summary()
    seats = fetch_seats()

    if metrics or usage or seats:
        build_summary_report(metrics, usage, seats)
        print("\n✅ All endpoints fetched successfully!")
    else:
        print("\n⚠️ No data retrieved — check permissions & plan.")
        raise SystemExit(1)

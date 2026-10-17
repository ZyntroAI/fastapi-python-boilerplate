#!/usr/bin/env python3
"""
📱 Phone Price Tracker — Status Dashboard
Usage:
  python dashboard.py          → Show full status
  python dashboard.py short    → Quick summary only
  python dashboard.py clear    → Clear old history/reports
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)

# ── Colors ────────────────────────────────────────────────
class Colors:
    OK = "\033[92m✅"
    WARN = "\033[93m⚠️"
    FAIL = "\033[91m❌"
    INFO = "\033[94mℹ️"
    BOLD = "\033[1m"
    RESET = "\033[0m"

# ── Checkers ──────────────────────────────────────────────
def check_service():
    """Check systemd service status"""
    try:
        out = subprocess.run(
            ["systemctl", "is-active", "--quiet", "phone-tracker.service"],
            capture_output=True
        )
        if out.returncode == 0:
            return True, "Running"
        return False, "Stopped"
    except:
        return None, "Not installed"

def check_process():
    """Check if Python process is running"""
    try:
        out = subprocess.run(
            ["pgrep", "-f", "entrypoint.py"],
            capture_output=True, text=True
        ).stdout.strip()
        if out:
            return True, out.split("\n")[0]
        return False, "—"
    except:
        return False, "—"

def check_env_vars():
    """Check .env configuration"""
    required = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing = [v for v in required if not os.getenv(v)]
    return missing

def check_history():
    """Check price history file"""
    h_path = "price_history.json"
    if not os.path.exists(h_path):
        return False, 0, "—"
    with open(h_path, encoding="utf-8") as f:
        data = json.load(f)
    return True, len(data), h_path

def check_reports():
    """List recent reports"""
    reports = sorted([f for f in os.listdir(".") if f.startswith("report_") and f.endswith(".md")], reverse=True)
    return reports[:5]  # Last 5

def get_next_run():
    """Calculate next scheduled run (every Friday 20:00 ICT)"""
    from datetime import timedelta
    now = datetime.now()
    days_ahead = 4 - now.weekday()  # Friday = 4
    if days_ahead <= 0:
        days_ahead += 7
    next_run = now + timedelta(days=days_ahead)
    next_run = next_run.replace(hour=20, minute=0, second=0, microsecond=0)
    return next_run.strftime("%Y-%m-%d %H:%M ICT")

# ── Display ───────────────────────────────────────────────
def print_header(title):
    print(f"\n{Colors.BOLD}┌─ {title} {'─'*(45-len(title))}┐{Colors.RESET}")

def print_footer():
    print(f"{Colors.BOLD}└{'─'*50}┘{Colors.RESET}")

def full_dashboard():
    os.system("cls" if os.name == "nt" else "clear")
    
    print(f"\n{Colors.BOLD}📱 PHONE PRICE TRACKER — STATUS DASHBOARD{Colors.RESET}")
    print(f"📂 Project: {PROJECT_DIR}")
    print(f"🕐 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ── System Status ─────────────────────────────────────
    print_header("SYSTEM STATUS")
    
    svc_ok, svc_status = check_service()
    proc_ok, proc_id = check_process()
    
    status_icon = Colors.OK if svc_ok else (Colors.WARN if svc_ok is None else Colors.FAIL)
    print(f"  {status_icon} Systemd Service:  {svc_status}")
    
    proc_icon = Colors.OK if proc_ok else Colors.FAIL
    print(f"  {proc_icon} Process Running:  {'Yes (PID: ' + proc_id + ')' if proc_ok else 'No'}")
    
    next_run = get_next_run()
    print(f"  {Colors.INFO} Next Scheduled:   {next_run}")
    print_footer()

    # ── Configuration ─────────────────────────────────────
    print_header("CONFIGURATION")
    missing = check_env_vars()
    if missing:
        print(f"  {Colors.FAIL} Missing: {', '.join(missing)}")
    else:
        print(f"  {Colors.OK} Telegram: Configured")
    
    threshold = os.getenv("ALERT_THRESHOLD_PCT", "5")
    absolute = os.getenv("ALERT_ABSOLUTE_BELOW", "0")
    print(f"  {Colors.INFO} Alert Threshold:  {threshold}% drop")
    if float(absolute) > 0:
        print(f"  {Colors.INFO} Price Below:     ฿{absolute}")
    print_footer()

    # ── Data ──────────────────────────────────────────────
    print_header("DATA & HISTORY")
    hist_ok, hist_count, hist_path = check_history()
    if hist_ok:
        print(f"  {Colors.OK} History File:    {hist_path}")
        print(f"  {Colors.INFO} Records Stored:  {hist_count} price checks")
    else:
        print(f"  {Colors.WARN} No history yet — run a check first")
    
    reports = check_reports()
    if reports:
        print(f"  {Colors.INFO} Recent Reports:  {len(reports)} total")
        for r in reports[:3]:
            print(f"      • {r}")
    else:
        print(f"  {Colors.WARN} No reports yet")
    print_footer()

    # ── Quick Actions ──────────────────────────────────────
    print_header("QUICK COMMANDS")
    print("  python entrypoint.py once   → Run price check now")
    print("  systemctl status phone-tracker.service → View logs")
    print("  journalctl -u phone-tracker.service -f → Live logs")
    print_footer()

def short_summary():
    """Minimal one-line status"""
    svc_ok, _ = check_service()
    proc_ok, _ = check_process()
    hist_ok, hist_count, _ = check_history()
    next_run = get_next_run()
    
    svc = "✅ Service" if svc_ok else "⏹️ Service"
    proc = "✅ Running" if proc_ok else "⏹️ Not running"
    hist = f"📊 {hist_count} records" if hist_ok else "📊 No data"
    
    print(f"{svc} | {proc} | {hist} | 🕐 Next: {next_run}")

def clear_old():
    """Clear old reports & history"""
    confirm = input("⚠️ Clear history and old reports? (y/N): ").lower().strip()
    if confirm == "y":
        for f in os.listdir("."):
            if f.startswith("report_") and f.endswith(".md"):
                os.remove(f)
                print(f"  🗑️ Deleted {f}")
        if os.path.exists("price_history.json"):
            os.remove("price_history.json")
            print("  🗑️ Deleted price_history.json")
        print("✅ Cleared!")
    else:
        print("Cancelled")

# ── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    
    if mode == "short":
        short_summary()
    elif mode == "clear":
        clear_old()
    else:
        full_dashboard()

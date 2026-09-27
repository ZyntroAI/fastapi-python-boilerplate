Here's the clean, standalone entry point — ready to drop in and run 👇



 entrypoint.py  — Standalone Launcher

python
#!/usr/bin/env python3
"""
📱 Phone Price Tracker — Entry Point
Usage:
python entrypoint.py → start scheduler (every Fri 20:00 ICT)
python entrypoint.py once → run immediately, no wait
python entrypoint.py test → verify Telegram & .env setup
"""

import sys
import os
from dotenv import load_dotenv

── Load config first ─────────────────────────────────────
load_dotenv()

def print_banner():
print("=" * 50)
print("📱 PHONE PRICE TRACKER — ENTRY POINT")
print("=" * 50)
print()

def check_env():
"""Validate .env configuration"""
missing = []

# Telegram
if not os.getenv("TELEGRAM_BOT_TOKEN"):
missing.append("TELEGRAM_BOT_TOKEN")
if not os.getenv("TELEGRAM_CHAT_ID"):
missing.append("TELEGRAM_CHAT_ID")

# Thresholds
if not os.getenv("ALERT_THRESHOLD_PCT"):
print("⚠️ ALERT_THRESHOLD_PCT not set → using default 5%")
if not os.getenv("ALERT_ABSOLUTE_BELOW"):
print("⚠️ ALERT_ABSOLUTE_BELOW not set → using default 0 (disabled)")

if missing:
print("❌ Missing required variables in .env:")
for m in missing:
print(f" - {m}")
print("\n💡 Get them from Telegram:")
print(" 1. TELEGRAM_BOT_TOKEN → @BotFather → /newbot")
print(" 2. TELEGRAM_CHAT_ID → @userinfobot")
return False
return True

def test_telegram():
"""Send a test message to verify bot works"""
import requests

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print("📡 Testing Telegram connection...")
try:
resp = requests.post(
f"https://api.telegram.org/bot{token}/sendMessage",
data={
"chat_id": chat_id,
"text": "✅ Phone Price Tracker is ONLINE\n\n"
"Will check prices every Friday at 8 PM ICT.\n"
"You're all set! 🚀",
"parse_mode": "Markdown"
},
timeout=15
)
data = resp.json()
if data.get("ok"):
print("✅ SUCCESS — Message sent! Check your Telegram 📱")
else:
print(f"⚠️ API Error: {data}")
except Exception as e:
print(f"❌ Failed: {e}")

def run_now():
"""Import and execute the main tracker immediately"""
try:
from phone_price_tracker import run_check
run_check()
except ImportError as e:
print(f"❌ Cannot import phone_price_tracker: {e}")
print("💡 Make sure phone_price_tracker.py is in the same folder")

def start_scheduler():
"""Start the weekly scheduled job"""
try:
from phone_price_tracker import start_scheduler
start_scheduler()
except ImportError as e:
print(f"❌ Cannot import phone_price_tracker: {e}")

── Main Flow ──────────────────────────────────────────────
if name == "main":
print_banner()

# Load .env early so checks work
if not os.path.exists(".env"):
print("⚠️ .env file not found — create it from .env.example")
print(" Continuing anyway...\n")

mode = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "scheduler"

if mode == "test":
print("🔍 Running configuration test...\n")
check_env()
print()
test_telegram()

elif mode == "once":
if not check_env():
print("\n⚠️ Config incomplete — proceeding anyway...\n")
print("🚀 Running price check NOW...\n")
run_now()

elif mode in ("scheduler", ""):
if not check_env():
print("\n⚠️ Incomplete config — alerts may not send.\n")
print("📅 Starting scheduler — Every Friday 20:00 ICT\n")
start_scheduler()

else:
print("❓ Unknown command. Usage:")
print(" python entrypoint.py → Start scheduler")
print(" python entrypoint.py once → Run immediately")
print(" python entrypoint.py test → Test Telegram & config")
sys.exit(1)




📁 Your Folder Structure Should Be

plaintext
your-project-folder/
├── .env ← Your tokens & settings here
├── phone_price_tracker.py ← The main script
└── entrypoint.py ← ← NEW — run this one!




🚀 How to Use

1️⃣ Test Your Setup First ✅

bash
python entrypoint.py test


• Validates  .env  values
• Sends a confirmation message to your Telegram
• Confirms everything connects

2️⃣ Run Immediately (One-Shot)

bash
python entrypoint.py once


• Checks prices right now
• Sends alerts if thresholds triggered
• Saves report & history

3️⃣ Start Scheduled Mode (Keep Running)

bash
python entrypoint.py


• Runs in background
• Every Friday at 20:00 ICT → auto-checks & alerts
• Press  Ctrl+C  to stop



⚙️ Quick  .env  Reminder

env
ALERT_THRESHOLD_PCT=5
ALERT_ABSOLUTE_BELOW=45000
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=987654321


No extra spaces around  =  signs — that's the #1 cause of failures!



Want me to add auto-restart on crash or systemd/service file so it runs automatically on server boot? 🚀

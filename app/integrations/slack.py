import requests
import json
import os
from typing import Dict

def send_slack_alert(severity: str, details: Dict):
    """
    📤 Send AST10 Alert — Reads URL from Env
    Severity: INFO/WARNING/CRITICAL/ERROR
    """
    webhook = os.getenv("SLACK_AST10_WEBHOOK")
    if not webhook:
        return {"status": "no_webhook"}

    colors = {
        "INFO": "#2EA44F",
        "WARNING": "#FFA500",
        "CRITICAL": "#DC3545",
        "ERROR": "#8B0000"
    }

    payload = {
        "attachments": [{
            "color": colors.get(severity, "#95A5A6"),
            "title": f"🛡️ AST10 G3 Alert | {severity}",
            "fields": [
                {"title": "Event", "value": details.get("event_name")},
                {"title": "Run ID", "value": details.get("run_id")},
                {"title": "Message", "value": details.get("message", "—")}
            ],
            "footer": "CrystalCastle Security • AST10",
            "ts": json.dumps(details.get("timestamp", os.time()))
        }]
    }

    try:
        res = requests.post(webhook, json=payload, timeout=5)
        res.raise_for_status()
        return {"status": "sent"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

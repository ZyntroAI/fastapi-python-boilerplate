"""Slack alert — stdlib-only (urllib). No-op when webhook unset/disabled."""
from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, Optional

from .config import SLACK_WEBHOOK_URL


def send_alert(title: str, detail: str, payload: Optional[Dict[str, Any]] = None,
               webhook: str = "") -> bool:
    """Send a Slack alert. Returns True if posted, False if disabled/no-op.

    Raises on network error so callers can decide whether to fail or swallow.
    """
    url = webhook or SLACK_WEBHOOK_URL
    if not url:
        return False  # disabled — safe no-op
    text = f"*{title}*\n```\n{detail}\n```"
    if payload is not None:
        text += f"\nData: `{str(payload)[:200]}`..."
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status == 200

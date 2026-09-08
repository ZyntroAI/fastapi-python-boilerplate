"""Agent security suite config — env-driven, safe defaults."""
from __future__ import annotations

import os


def _get(name: str, default: str) -> str:
    return os.getenv(name, default)


# Audit log location (SQLite file). Path relative to the suite root.
AUDIT_DB_PATH = _get("AUDIT_DB_PATH", "agent_security_suite/audit_logs.db")

# Slack webhook — empty = alerts disabled (safe no-op).
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

SCHEMA_VERSION = "1.0.0"

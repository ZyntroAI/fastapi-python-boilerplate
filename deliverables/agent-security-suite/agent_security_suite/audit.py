"""ISO-27001-style audit log backed by SQLite (stdlib only).

Writes an immutable append-only event per action with a payload SHA-256
fingerprint, so a log row can be verified against the original payload.
"""
from __future__ import annotations

import hashlib
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .config import AUDIT_DB_PATH


def _connect() -> sqlite3.Connection:
    Path(AUDIT_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(AUDIT_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id TEXT UNIQUE,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                agent_id TEXT,
                action_type TEXT NOT NULL,
                resource_path TEXT,
                status TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                payload_snippet TEXT,
                error_msg TEXT,
                checkpoint_id TEXT,
                approver_id TEXT
            )
            """
        )


def _hash(payload: Any) -> str:
    return hashlib.sha256(str(payload).encode("utf-8")).hexdigest()


def log_event(
    session_id: str,
    agent_id: str,
    action_type: str,
    resource: str,
    status: str,
    payload: Dict[str, Any],
    error: Optional[str] = None,
    checkpoint: Optional[str] = None,
    approver: Optional[str] = None,
) -> str:
    """Append an audit event; returns the event's log_id."""
    init_db()
    payload_str = str(payload)
    log_id = str(uuid.uuid4())
    snippet = payload_str[:250] + ("..." if len(payload_str) > 250 else "")
    ts = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_log
              (log_id, timestamp, session_id, agent_id, action_type, resource_path,
               status, payload_hash, payload_snippet, error_msg, checkpoint_id, approver_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (log_id, ts, session_id, agent_id, action_type, resource, status,
             _hash(payload), snippet, error, checkpoint, approver),
        )
    return log_id


def verify_row(log_id: str, payload: Any) -> bool:
    """Verify a stored event's payload hash still matches (integrity check)."""
    with _connect() as conn:
        row = conn.execute("SELECT payload_hash FROM audit_log WHERE log_id=?", (log_id,)).fetchone()
    return bool(row) and row["payload_hash"] == _hash(payload)

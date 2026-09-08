# Agent Security Suite — Runnable Core

ISO-27001-style audit log + JSON schema validation + Slack alert.

## Modules
- `agent_security_suite/audit.py` — append-only SQLite audit log with per-event
  SHA-256 payload hash; `verify_row()` checks integrity (tamper detection).
- `agent_security_suite/validation.py` — JSON-schema validation (`validate_crm_data`,
  generic `validate_against`) that audits every outcome and alerts on failure.
- `agent_security_suite/slack_alert.py` — stdlib-only (urllib) alert; no-op when
  `SLACK_WEBHOOK_URL` is unset (safe for local/CI).

## Usage
```python
from agent_security_suite import validate_crm_data
res = validate_crm_data({"customer_name": "Acme", "deal_value": 250}, "sess1", "agent1")
# -> {"status": "verified", "valid": True}; failure audits + alerts instead
```

## Config (env)
- `AUDIT_DB_PATH` — SQLite path (default `agent_security_suite/audit_logs.db`)
- `SLACK_WEBHOOK_URL` — set to enable Slack alerts (empty = disabled)

## Run tests
```bash
python -m pytest tests/ -q    # 7 passed
```

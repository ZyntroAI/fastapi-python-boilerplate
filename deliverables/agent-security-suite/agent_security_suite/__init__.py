"""Agent Security Suite — full runnable stack.

Core (no extra deps): audit log (ISO-27001-style) + JSON schema validation +
Slack alert (stdlib-only). Optional (lazy-import): LangGraph time-travel
recovery + MCP client — only needed when those packages are installed.

Example:
    from agent_security_suite import validate_crm_data
    res = validate_crm_data({"customer_name": "Acme", "deal_value": 100}, "s1", "agent1")
"""
from .audit import init_db, log_event, verify_row
from .validation import CRM_SCHEMA, validate_against, validate_crm_data
from . import ci_ops  # permission-aware + SHA-pin scan + CI fingerprint

__all__ = ["init_db", "log_event", "verify_row", "validate_crm_data",
           "validate_against", "CRM_SCHEMA", "ci_ops"]

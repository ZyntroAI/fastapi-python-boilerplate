"""Agent Security Suite — full runnable stack.

Core (no extra deps): audit log (ISO-27001-style) + JSON schema validation +
Slack alert (stdlib-only). Optional (lazy-import): LangGraph time-travel
recovery, MCP client, RunPod client — only loaded when those packages/keys are
actually used.

Example:
    from agent_security_suite import validate_crm_data, connect_runpod
    res = validate_crm_data({"customer_name": "Acme", "deal_value": 100}, "s1", "agent1")
"""
from .audit import init_db, log_event, verify_row
from .validation import CRM_SCHEMA, validate_against, validate_crm_data
from . import ci_ops  # permission-aware + SHA-pin scan + CI fingerprint
from .runpod_client import RunPodClient, connect_runpod  # lazy runpod import

__all__ = ["init_db", "log_event", "verify_row", "validate_crm_data",
           "validate_against", "CRM_SCHEMA", "ci_ops", "RunPodClient",
           "connect_runpod"]

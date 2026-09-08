"""Agent Security Suite — runnable core.

audit log (ISO-27001-style) + JSON schema validation + Slack alert.
Stdlib-first: audit & alert use only the standard library; validation uses
the `jsonschema` package.

Example:
    from agent_security_suite import validate_crm_data
    res = validate_crm_data({"customer_name": "Acme", "deal_value": 100}, "s1", "agent1")
"""
from .audit import init_db, log_event, verify_row
from .validation import CRM_SCHEMA, validate_against, validate_crm_data

__all__ = ["init_db", "log_event", "verify_row", "validate_crm_data",
           "validate_against", "CRM_SCHEMA"]

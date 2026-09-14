"""JSON schema validation for structured data (jsonschema lib)."""
from __future__ import annotations

from typing import Any, Dict

from jsonschema import ValidationError, validate

from .audit import log_event
from .slack_alert import send_alert

# CRM record schema — a representative example the suite validates.
CRM_SCHEMA = {
    "type": "object",
    "properties": {
        "customer_name": {"type": "string", "minLength": 1},
        "deal_value": {"type": "number", "minimum": 0},
        "source": {"type": "string"},
    },
    "required": ["customer_name", "deal_value"],
}


def validate_crm_data(data: Dict[str, Any], session_id: str, agent_id: str) -> Dict[str, Any]:
    """Validate a CRM payload against CRM_SCHEMA; audit + alert on failure.

    Returns {"status": "verified"|"error", "valid": bool, ...}.
    """
    try:
        validate(instance=data, schema=CRM_SCHEMA)
    except ValidationError as e:
        err = str(e)
        log_event(session_id, agent_id, "VALIDATE", "CRM_DATA", "FAILED", data, error=err)
        send_alert("CRM Validation Failed", err, data)
        return {"status": "error", "valid": False, "error": err}
    log_event(session_id, agent_id, "VALIDATE", "CRM_DATA", "SUCCESS", data)
    return {"status": "verified", "valid": True}


def validate_against(data: Dict[str, Any], schema: Dict[str, Any],
                     session_id: str, agent_id: str,
                     resource: str = "DATA") -> Dict[str, Any]:
    """Generic JSON-schema validation wrapper with audit on both outcomes."""
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        err = str(e)
        log_event(session_id, agent_id, "VALIDATE", resource, "FAILED", data, error=err)
        return {"status": "error", "valid": False, "error": err}
    log_event(session_id, agent_id, "VALIDATE", resource, "SUCCESS", data)
    return {"status": "verified", "valid": True}

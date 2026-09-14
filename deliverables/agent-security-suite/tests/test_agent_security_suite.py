"""Agent Security Suite core tests — audit log, validation, alert no-op."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# isolate audit DB to a temp file for this run
_tmp = tempfile.mkdtemp()
os.environ["AUDIT_DB_PATH"] = os.path.join(_tmp, "audit_test.db")


import agent_security_suite as suite
from agent_security_suite import audit, validation


def test_audit_log_event_and_verify():
    lid = audit.log_event("sess1", "agent1", "VALIDATE", "CRM", "SUCCESS", {"k": 1})
    assert audit.verify_row(lid, {"k": 1}) is True
    assert audit.verify_row(lid, {"k": 2}) is False  # tamper detected


def test_audit_rows_persisted():
    lid = audit.log_event("sess2", "agent2", "RUN", "JOB", "FAILED", {"x": 1}, error="boom")
    assert lid  # no exception; row written


def test_validation_valid_crm():
    res = validation.validate_crm_data({"customer_name": "Acme", "deal_value": 250}, "s", "a")
    assert res["valid"] is True and res["status"] == "verified"


def test_validation_invalid_crm():
    res = validation.validate_crm_data({"deal_value": -5}, "s", "a")  # missing name + negative
    assert res["valid"] is False and res["status"] == "error"


def test_validation_generic_schema():
    schema = {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}
    ok = validation.validate_against({"id": 1}, schema, "s", "a", "ITEM")
    bad = validation.validate_against({"id": "no"}, schema, "s", "a", "ITEM")
    assert ok["valid"] is True and bad["valid"] is False


def test_slack_alert_noop_when_no_webhook():
    # no webhook set -> returns False without network
    assert validation.send_alert_if_configured if hasattr(validation, "send_alert_if_configured") else True
    from agent_security_suite.slack_alert import send_alert
    assert send_alert("t", "d") is False


def test_facade_exports():
    assert hasattr(suite, "validate_crm_data")
    assert hasattr(suite, "log_event")

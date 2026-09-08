"""Extension sub-skill tests — validate, guide, verify, security, provenance, knowledge."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from notebooklm_access import (validate_share, remediation_steps, next_action,
                               check_link, ProvenanceLog, build_knowledge_artifact)

NB = "c763d2b6-f074-4090-95cc-03d2592253bd"
BASE = f"https://notebooklm.google.com/notebook/{NB}"


# validate
def test_validate_share_public():
    r = validate_share(BASE, ["ok_200_anon"])
    assert r["share_state"] == "PUBLIC_OK" and r["valid"] is True


def test_validate_share_restricted():
    r = validate_share(BASE, ["login_page_detected"])
    assert r["share_state"] == "NOT_PUBLIC" and r["valid"] is False


def test_validate_share_invalid_url():
    r = validate_share("https://evil.example.com/x", ["ok_200_anon"])
    assert r["share_state"] == "URL_INVALID"


# guide
def test_remediation_steps():
    s = remediation_steps()
    assert "set_anyone_with_link" in s and "role_viewer" in s


def test_next_action_restricted():
    a = next_action("RESTRICTED")
    assert a["type"] == "CHANGE_SHARING" and a["actor"] == "OWNER"


# security
def test_check_link_https_clean():
    assert check_link(BASE)["safe"] is True


def test_check_link_tracking_unsafe():
    r = check_link(BASE + "?utm_source=x")
    assert r["safe"] is False and r["tracking_stripped"] is True


def test_check_link_rejects_creds():
    r = check_link("https://user:pass@notebooklm.google.com/x")
    assert r["no_credentials"] is False and r["safe"] is False


# provenance
def test_provenance_log():
    log = ProvenanceLog()
    log.record(BASE, "probe", "RESTRICTED", ["login_page_detected"])
    assert len(log.rows()) == 1
    assert log.rows()[0]["result"] == "RESTRICTED"
    assert "timestamp" in log.rows()[0]


# knowledge
def test_build_knowledge_artifact():
    a = build_knowledge_artifact(BASE, {"provider": "notebooklm"})
    assert a["artifact_id"] and a["canonical_url"] == BASE
    assert a["registered"] is True

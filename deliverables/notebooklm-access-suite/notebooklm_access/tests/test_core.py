"""Core P0 tests — resolver, access, artifact."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import pytest
from notebooklm_access import resolver, access, artifact
from notebooklm_access.resolver import ResolverError

NB = "c763d2b6-f074-4090-95cc-03d2592253bd"
ART = "9258650d-003b-4694-ba82-4dff15ea98e"
BASE = f"https://notebooklm.google.com/notebook/{NB}"
RAW = f"{BASE}/artifact/{ART}?utm_source=nlmm_share"


# --- resolver ---
def test_resolve_artifact_url_canonical():
    r = resolver.resolve(RAW)
    assert r["resource"]["notebook_id"] == NB
    assert r["resource"]["artifact_id"] == ART
    assert r["resource"]["canonical_url"] == BASE
    assert r["resource"]["tracking_removed"] is True


def test_resolve_plain_canonical():
    r = resolver.resolve(BASE)
    assert r["resource"]["canonical_url"] == BASE
    assert r["resource"]["artifact_id"] is None


def test_resolver_rejects_wrong_host():
    with pytest.raises(ResolverError):
        resolver.normalize(f"https://evil.example.com/notebook/{NB}")


def test_extract_artifact():
    assert resolver.extract_artifact(RAW) == ART
    assert resolver.extract_artifact(BASE) is None


# --- artifact ---
def test_route_artifact_to_notebook():
    r = artifact.route_artifact(RAW)
    assert r["routed"] is True
    assert r["reason"] == "artifact_to_notebook"
    assert r["canonical_url"] == BASE
    assert r["artifact_metadata"]["artifact_id"] == ART


def test_route_no_artifact():
    r = artifact.route_artifact(BASE)
    assert r["routed"] is False and r["reason"] == "no_artifact"


def test_artifact_metadata_none():
    assert artifact.artifact_metadata(BASE) is None


# --- access (evidence-based classification) ---
def test_access_restricted_on_login_evidence():
    a = access.classify_access(["login_redirect", "artifact_denied"])
    assert a["state"] == "RESTRICTED"
    assert a["anonymous"] is False and a["login_required"] is True


def test_access_public_on_anon_ok():
    a = access.classify_access(["ok_200_anon"])
    assert a["state"] == "PUBLIC" and a["anonymous"] is True


def test_access_private_wins_over_public():
    a = access.classify_access(["ok_200_anon", "requires_account"])
    assert a["state"] == "PRIVATE"


def test_access_invalid_evidence_empty():
    a = access.classify_access([])
    assert a["state"] == "UNKNOWN"


def test_report_access_restricted():
    rep = access.report(["login_page_detected"])
    assert rep["status"]["code"] == "ACCESS_RESTRICTED"
    assert rep["status"]["user_action_required"] is True

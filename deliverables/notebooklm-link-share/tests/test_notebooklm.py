"""NotebookLM link-share skill tests."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from notebooklm_link_share import (normalize_link, validate_link, generate_share_text,
                                   is_valid_uuid, public_skill, NotebookLMError)

UUID = "c763d2b6-f074-4090-95cc-03d2592253bd"
SUB = "7f72e937-9018-4a11-9f4b-0952ad1601ff"
CLEAN = f"https://notebooklm.google.com/notebook/{UUID}"


def test_normalize_artifact_and_params():
    raw = f"{CLEAN}/artifact/{SUB}?utm_source=nlmm_share&utm_campaign=x#frag"
    assert normalize_link(raw) == CLEAN


def test_normalize_without_scheme():
    assert normalize_link(f"notebooklm.google.com/notebook/{UUID}") == CLEAN


def test_normalize_plain_clean():
    assert normalize_link(CLEAN) == CLEAN


def test_rejects_wrong_host():
    with pytest.raises(NotebookLMError):
        normalize_link("https://evil.example.com/notebook/%s" % UUID)


def test_rejects_missing_uuid():
    with pytest.raises(NotebookLMError):
        normalize_link("https://notebooklm.google.com/notebook/nope")


def test_uuid_format():
    assert is_valid_uuid(UUID) is True
    assert is_valid_uuid("short") is False


def test_validate_clean_link():
    v = validate_link(CLEAN)
    assert v["valid"] is True
    assert v["recommendation"] == "Share ready"


def test_generate_templates():
    short = generate_share_text(CLEAN, "short", title="My Doc")
    assert "My Doc" in short and CLEAN in short
    formal = generate_share_text(CLEAN, "formal")
    assert "View-Only" in formal and CLEAN in formal
    with pytest.raises(NotebookLMError):
        generate_share_text(CLEAN, "bogus")


def test_public_skill_full():
    res = public_skill(f"{CLEAN}/artifact/{SUB}?utm_source=x", style="short", title="Doc")
    assert res["clean_url"] == CLEAN
    assert res["validation"]["valid"] is True
    assert CLEAN in res["share_template"]

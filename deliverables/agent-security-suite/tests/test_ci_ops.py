"""ci_ops module tests — permission-aware, SHA-pin scan, CI fingerprint."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_tmp = tempfile.mkdtemp()
os.environ["AUDIT_DB_PATH"] = os.path.join(_tmp, "audit_test.db")

from pathlib import Path
from agent_security_suite import ci_ops


# --- permission-aware ---
def test_workflow_write_needs_workflows_perm():
    # contents:write alone is NOT enough for workflow_write (real lesson)
    granted = {"contents:write"}
    assert ci_ops.can_write("workflow_write", granted) is False
    assert ci_ops.can_write("normal_code_write", granted) is True


def test_explain_lists_missing():
    ex = ci_ops.explain("workflow_write", {"contents:write"})
    assert ex["allowed"] is False
    assert "workflows:write" in ex["missing"]


def test_rerun_ci_needs_actions():
    assert ci_ops.can_write("rerun_ci", {"actions:write"}) is True
    assert ci_ops.can_write("rerun_ci", {"contents:write"}) is False


# --- SHA-pin scan ---
SAMPLE = """\
name: ci
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@a5ac7e51b41094c92402da3b24376905afc3c1d8
"""


def test_sha_pin_scan_flags_tag_and_accepts_sha():
    res = ci_ops.sha_pin_scan(SAMPLE)
    assert res["compliant"] is False          # @v4 is not pinned
    assert res["total"] == 2
    assert res["unpinned"][0]["action"] == "actions/checkout"
    assert res["unpinned"][0]["ref"] == "v4"


def test_sha_pin_scan_fully_pinned():
    text = "uses: actions/checkout@a5ac7e51b41094c92402da3b24376905afc3c1d8"
    res = ci_ops.sha_pin_scan(text)
    assert res["compliant"] is True and res["unpinned"] == []


def test_sha_pin_scan_file(tmp_path):
    p = tmp_path / "wf.yml"
    p.write_text(SAMPLE)
    res = ci_ops.sha_pin_scan_file(Path(p))
    assert res["total"] == 2
    # missing file -> error, not crash
    bad = ci_ops.sha_pin_scan_file(Path("/no/such/file.yml"))
    assert "error" in bad and bad["compliant"] is False


# --- CI root-cause fingerprint ---
def test_fingerprint_sha_pin_policy():
    log = "Error: refusing to allow a GitHub App without workflows permission"
    assert ci_ops.fingerprint_failure(log) == "SHA_PIN_POLICY"


def test_fingerprint_unknown():
    assert ci_ops.fingerprint_failure("random test failure line") is None


def test_diagnose_batch_systemic():
    logs = [
        "refusing to allow a GitHub App without workflows permission on wf.yml",
        "refusing to allow a GitHub App without workflows permission on ci.yml",
        "refusing to allow a GitHub App without workflows permission on sec.yml",
    ]
    res = ci_ops.diagnose_batch(logs)
    assert res["systemic"] is True
    assert res["root_cause"] == "SHA_PIN_POLICY"


def test_diagnose_batch_not_systemic():
    res = ci_ops.diagnose_batch(["random a", "random b"])
    assert res["systemic"] is False

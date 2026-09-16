"""Git operations: patch diagnosis and EOL risk auditing."""

from __future__ import annotations

import json
from pathlib import Path

from patchsuite import gitops


def test_diagnose_whitespace_error():
    diag = gitops.diagnose_patch_failure(
        "error: patch failed: f.php:1\nerror: f.php: patch does not apply\n"
        "warning: 1 line adds whitespace errors.",
        1,
    )
    assert diag.applies is False
    assert "Whitespace" in diag.likely_cause
    assert "nowarn" in diag.suggested_fix


def test_diagnose_index_mismatch():
    diag = gitops.diagnose_patch_failure(
        "error: patch failed: x.yml:7\nerror: Did you hand edit your patch?\n"
        "It does not apply to blobs recorded in its index.",
        128,
    )
    assert diag.applies is False
    assert "blob" in diag.likely_cause.lower()


def test_diagnose_missing_path():
    diag = gitops.diagnose_patch_failure(
        "error: .github/workflows/x.yml: does not exist in index", 1
    )
    assert "not present on this branch" in diag.likely_cause


def test_diagnose_existing_path():
    diag = gitops.diagnose_patch_failure("error: foo.md: already exists", 1)
    assert "already there" in diag.likely_cause


def test_diagnose_malformed_patch_blames_eol():
    diag = gitops.diagnose_patch_failure("error: corrupt patch at line 12", 1)
    assert "malformed" in diag.likely_cause.lower()
    assert "CRLF" in diag.suggested_fix


def test_diagnose_unknown_error_says_so():
    diag = gitops.diagnose_patch_failure("error: something entirely new", 3)
    assert diag.applies is False
    assert "Unclassified" in diag.likely_cause
    assert diag.code == 3


def test_diagnosis_as_dict_is_json_safe():
    diag = gitops.diagnose_patch_failure("error: corrupt patch at line 1", 1)
    assert json.loads(json.dumps(diag.as_dict()))["applies"] is False


def test_git_available_and_not_a_work_tree(tmp_path: Path):
    assert gitops.git_available() is True
    assert gitops.is_work_tree(tmp_path) is False


def test_git_available_in_sandbox(git_sandbox):
    root, _ = git_sandbox
    assert gitops.is_work_tree(root) is True
    assert gitops.current_branch(root) == "main"
    assert len(gitops.head_sha(root, short=False)) == 40


def test_working_tree_state_clean_then_dirty(git_sandbox):
    root, git = git_sandbox
    (root / "a.txt").write_text("one\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    assert gitops.working_tree_state(root).dirty is False
    (root / "b.txt").write_text("two\n")
    state = gitops.working_tree_state(root)
    assert state.dirty is True
    assert any("b.txt" in e for e in state.entries)


def test_check_patch_on_a_missing_patch_file(git_sandbox):
    root, _ = git_sandbox
    diag = gitops.check_patch(Path("/nonexistent/x.patch"), root)
    assert diag.applies is False


def test_audit_eol_risk_flags_crlf_without_trailing_newline(tmp_path: Path):
    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    (wf / "bad.yml").write_bytes(b"name: x\r\non: push:")  # CRLF, unterminated
    (wf / "ok.yml").write_bytes(b"name: x\non: push\n")
    risks = {r.path: r for r in gitops.audit_eol_risk(tmp_path)}
    assert risks[".github/workflows/bad.yml"].at_risk is True
    assert risks[".github/workflows/ok.yml"].at_risk is False


def test_audit_eol_risk_reason_names_the_git_am_symptom(tmp_path: Path):
    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    (wf / "bad.yml").write_bytes(b"name: x\r\non: push:")
    risk = gitops.audit_eol_risk(tmp_path)[0]
    assert "git am" in risk.reason
    assert "git apply --check" in risk.reason


def test_audit_eol_risk_on_the_broken_fixture(fixtures: Path):
    risks = gitops.audit_eol_risk(fixtures / "broken-project")
    at_risk = {r.path for r in risks if r.at_risk}
    assert ".github/workflows/crlf-unterminated.yml" in at_risk


def test_audit_eol_risk_on_the_clean_fixture(fixtures: Path):
    risks = gitops.audit_eol_risk(fixtures / "clean-project")
    assert all(not r.at_risk for r in risks)


def test_audit_eol_risk_reports_mixed_endings_as_risky_for_patching(tmp_path: Path):
    d = tmp_path / "notes"
    d.mkdir()
    (d / "legacy.yml").write_bytes(b"a\r\nb\nc\r\n")
    risk = gitops.audit_eol_risk(tmp_path)[0]
    assert risk.eol == "mixed"
    assert risk.at_risk is False  # has a trailing newline, so only patch-fidelity matters
    assert "EOL" in risk.reason


def test_eol_risk_as_dict_is_json_safe(tmp_path: Path):
    (tmp_path / "a.yml").write_bytes(b"x\r\ny:")
    assert json.loads(json.dumps(gitops.audit_eol_risk(tmp_path)[0].as_dict()))["at_risk"] is True


def test_apply_patch_on_a_generated_patch(git_sandbox):
    """End-to-end: commit, diff, reset, re-apply."""
    root, git = git_sandbox
    target = root / "notes.md"
    target.write_text("one\n")
    git("add", "-A")
    git("commit", "-qm", "base")

    target.write_text("one\ntwo\n")
    diff = git("diff").stdout
    patch = root / "change.patch"
    patch.write_text(diff)

    git("checkout", "--", "notes.md")
    assert target.read_text() == "one\n"

    diag = gitops.check_patch(patch, root)
    assert diag.applies is True

    result = gitops.apply_patch(patch, root)
    assert result.ok is True
    assert target.read_text() == "one\ntwo\n"

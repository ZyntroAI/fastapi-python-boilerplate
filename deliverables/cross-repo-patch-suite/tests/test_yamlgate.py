"""Workflow YAML validation and SHA-pin auditing."""

from __future__ import annotations

import json
from pathlib import Path

from patchsuite import (
    audit_pins,
    find_action_refs,
    is_sha_pinned,
    validate_yaml_file,
)

REAL_SHA = "11bd71901bbe5b1630ceea73d27597364c9af683"


def test_valid_workflow_parses(fixtures: Path):
    check = validate_yaml_file(fixtures / "clean-project/.github/workflows/quality-gate.yml")
    assert check.valid is True
    assert check.error == ""


def test_unquoted_colon_is_reported_with_line(fixtures: Path):
    """The ScannerError case: a colon inside an unquoted scalar."""
    path = fixtures / "broken-project/.github/workflows/unquoted-colon.yml"
    check = validate_yaml_file(path)
    assert check.valid is False
    assert check.mark["line"] > 0
    assert ":x:" in check.problem
    assert "quote" in check.problem.lower()


def test_missing_file_is_invalid_not_an_exception(tmp_path: Path):
    check = validate_yaml_file(tmp_path / "nope.yml")
    assert check.valid is False
    assert check.error


def test_yaml_check_is_json_safe(fixtures: Path):
    check = validate_yaml_file(fixtures / "clean-project/.github/workflows/quality-gate.yml")
    assert json.loads(json.dumps(check.as_dict()))["valid"] is True


def test_quoted_colon_parses(tmp_path: Path):
    p = tmp_path / "q.yml"
    p.write_text('name: ok\njobs:\n  a:\n    steps:\n      - name: ":x:"\n        run: echo hi\n')
    assert validate_yaml_file(p).valid is True


def test_plain_value_colon_is_accepted(tmp_path: Path):
    """A normal mapping colon must not be flagged as a fault."""
    p = tmp_path / "m.yml"
    p.write_text("name: build\non: push\n")
    assert validate_yaml_file(p).valid is True


def test_find_action_refs_pinned_and_unpinned(tmp_path: Path):
    p = tmp_path / "w.yml"
    p.write_text(
        "jobs:\n  a:\n    steps:\n"
        f"      - uses: actions/checkout@{REAL_SHA}\n"
        "      - uses: actions/cache@v4\n"
    )
    refs = find_action_refs(p)
    assert len(refs) == 2
    assert refs[0].pinned is True
    assert refs[0].action == "actions/checkout"
    assert refs[1].pinned is False
    assert refs[1].ref == "v4"


def test_find_action_refs_skips_local_and_docker(tmp_path: Path):
    p = tmp_path / "w.yml"
    p.write_text("jobs:\n  a:\n    steps:\n      - uses: ./.github/actions/x\n      - uses: docker://alpine:3\n")
    assert find_action_refs(p) == []


def test_find_action_refs_reads_quoted_uses(tmp_path: Path):
    p = tmp_path / "w.yml"
    p.write_text(f'jobs:\n  a:\n    steps:\n      - uses: "actions/checkout@{REAL_SHA}"\n')
    refs = find_action_refs(p)
    assert len(refs) == 1
    assert refs[0].pinned is True


def test_is_sha_pinned_rejects_tags_and_partial_shas():
    assert is_sha_pinned(REAL_SHA) is True
    assert is_sha_pinned("v4") is False
    assert is_sha_pinned("main") is False
    assert is_sha_pinned(REAL_SHA[:7]) is False
    assert is_sha_pinned(REAL_SHA.upper()) is False


def test_audit_pins_flags_the_broken_fixture(fixtures: Path):
    audit = audit_pins(fixtures / "broken-project/.github/workflows")
    assert audit.compliant is False
    flagged = {r.ref for r in audit.unpinned}
    assert {"main", "v4", "v5"} <= flagged
    assert audit.pinned == 0, "nothing in the broken fixture should be pinned"


def test_audit_pins_passes_the_clean_fixture(fixtures: Path):
    audit = audit_pins(fixtures / "clean-project/.github/workflows")
    assert audit.compliant is True
    assert audit.unpinned == []
    assert audit.total_refs == 2
    assert audit.pinned == 2


def test_audit_pins_as_dict_is_json_safe(fixtures: Path):
    audit = audit_pins(fixtures / "broken-project/.github/workflows")
    payload = json.loads(json.dumps(audit.as_dict()))
    assert payload["compliant"] is False
    assert len(payload["unpinned"]) == len(audit.unpinned)


def test_audit_pins_ignores_git_directory(tmp_path: Path):
    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    (wf / "a.yml").write_text("jobs:\n  a:\n    steps:\n      - uses: actions/cache@v4\n")
    gitdir = tmp_path / ".git"
    gitdir.mkdir()
    (gitdir / "b.yml").write_text("jobs:\n  a:\n    steps:\n      - uses: actions/cache@v4\n")
    audit = audit_pins(tmp_path)
    assert audit.files_scanned == 1
    assert len(audit.unpinned) == 1


def test_mixed_refs_fixture_mixes_pinned_and_unpinned(fixtures: Path):
    audit = audit_pins(fixtures / "broken-project/.github/workflows")
    refs = [r for r in audit.unpinned]
    assert any(r.action == "actions/cache" for r in refs)
    assert any(r.action == "actions/upload-artifact" for r in refs)

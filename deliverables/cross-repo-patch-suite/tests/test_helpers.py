"""Helpers: the two scripts you run by hand."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SUITE_ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    path = SUITE_ROOT / "helpers" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"helpers_{name}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def safe_append():
    return _load("safe_append")


@pytest.fixture(scope="module")
def fix_eol():
    return _load("fix_eol")


# --- safe_append ----------------------------------------------------------


def test_safe_append_dry_run_writes_nothing(safe_append, tmp_path: Path):
    target = tmp_path / "f.md"
    target.write_bytes(b"one\r\n")
    report = safe_append.run(target, "two")
    assert target.read_bytes() == b"one\r\n"
    assert report["mode"] == "dry-run"


def test_safe_append_apply_preserves_crlf(safe_append, tmp_path: Path):
    target = tmp_path / "f.md"
    target.write_bytes(b"one\r\ntwo\r\n")
    report = safe_append.run(target, "three", apply=True)
    assert target.read_bytes() == b"one\r\ntwo\r\nthree\r\n"
    assert report["existing_eol"] == "crlf"
    assert report["safe"] is True
    assert report["diff"]["removed"] == 0


def test_safe_append_reports_no_removed_lines(safe_append, tmp_path: Path):
    target = tmp_path / "f.md"
    target.write_bytes(b"a\nb\n")
    report = safe_append.run(target, "c\nd", apply=True)
    assert report["diff"] == {"added": 2, "removed": 0, "total_touched": 2}


def test_safe_append_records_before_hash(safe_append, tmp_path: Path):
    target = tmp_path / "f.md"
    target.write_bytes(b"a\n")
    report = safe_append.run(target, "b")
    assert len(report["before_sha256"]) == 64


def test_safe_append_cli_dry_run_default(safe_append, tmp_path: Path):
    target = tmp_path / "f.md"
    target.write_bytes(b"a\n")
    rc = safe_append.main([str(target), "--text", "b"])
    assert rc == 0
    assert target.read_bytes() == b"a\n", "the CLI must not write without --apply"


def test_safe_append_cli_apply(safe_append, tmp_path: Path):
    target = tmp_path / "f.md"
    target.write_bytes(b"a\n")
    rc = safe_append.main([str(target), "--text", "b", "--apply"])
    assert rc == 0
    assert target.read_bytes() == b"a\nb\n"


def test_safe_append_cli_json(safe_append, tmp_path: Path, capsys):
    target = tmp_path / "f.md"
    target.write_bytes(b"a\n")
    safe_append.main([str(target), "--text", "b", "--json"])
    assert '"mode": "dry-run"' in capsys.readouterr().out


def test_safe_append_cli_requires_a_payload_source(safe_append, tmp_path: Path):
    target = tmp_path / "f.md"
    target.write_bytes(b"a\n")
    with pytest.raises(SystemExit):
        safe_append.main([str(target)])


# --- fix_eol --------------------------------------------------------------


def test_fix_eol_repair_to_crlf_closes_the_final_newline(fix_eol):
    raw = b"name: x\r\non: push:"
    out = fix_eol.repair_bytes(raw, "crlf")
    assert out.endswith(b"\r\n")
    assert out.startswith(b"name: x\r\n")
    assert b"\n" not in out.replace(b"\r\n", b"")


def test_fix_eol_repair_to_lf_normalises(fix_eol):
    out = fix_eol.repair_bytes(b"a\r\nb:", "lf")
    assert out == b"a\nb:\n"


def test_fix_eol_repair_adds_no_content(fix_eol):
    out = fix_eol.repair_bytes(b"a\r\nb:", "crlf")
    assert out.replace(b"\r\n", b"").replace(b"\n", b"") == b"ab:"


def test_fix_eol_dry_run_leaves_files_alone(fix_eol, tmp_path: Path):
    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    bad = wf / "bad.yml"
    bad.write_bytes(b"name: x\r\non: push:")
    before = bad.read_bytes()
    report = fix_eol.run(tmp_path, "crlf", apply=False)
    assert report["repaired"] == 1
    assert bad.read_bytes() == before


def test_fix_eol_apply_repairs_and_clears_the_risk(fix_eol, tmp_path: Path):
    from patchsuite import audit_eol_risk

    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    bad = wf / "bad.yml"
    bad.write_bytes(b"name: x\r\non: push:")
    report = fix_eol.run(tmp_path, "crlf", apply=True)
    assert report["applied"] is True
    assert audit_eol_risk(tmp_path)[0].at_risk is False
    assert bad.read_bytes().endswith(b"\r\n")


def test_fix_eol_skips_healthy_files(fix_eol, tmp_path: Path):
    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    (wf / "ok.yml").write_bytes(b"name: x\n")
    assert fix_eol.run(tmp_path, "crlf", apply=False)["repaired"] == 0


def test_fix_eol_diff_is_confined_to_the_final_line(fix_eol, tmp_path: Path):
    wf = tmp_path / ".github/workflows"
    wf.mkdir(parents=True)
    (wf / "bad.yml").write_bytes(b"a\r\nb\r\nc:")
    report = fix_eol.run(tmp_path, "crlf", apply=False)
    # Closing an unterminated final line registers as that one line changing —
    # never as a rewrite of the whole file.
    assert report["files"][0]["diff"]["total_touched"] == 2
    assert report["files"][0]["diff"]["removed"] == 1
    assert report["files"][0]["final_newline_after"] is True


def test_fix_eol_cli_dry_run(fix_eol, tmp_path: Path):
    wf = tmp_path / "w"
    wf.mkdir()
    (wf / "bad.yml").write_bytes(b"a\r\nb:")
    assert fix_eol.main([str(wf)]) == 0
    assert (wf / "bad.yml").read_bytes() == b"a\r\nb:"

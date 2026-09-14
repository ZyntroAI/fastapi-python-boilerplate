"""Tests for verify-pins.py.

Each case corresponds to a way the verifier could give a wrong answer rather
than merely fail — false "fake" verdicts are the expensive direction, because
they send someone to replace a pin that was already correct.

The module filename contains a hyphen, so it cannot be imported by name; it is
loaded from its path.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("verify_pins", SKILL / "verify-pins.py")
verify_pins = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify_pins)


# ---- owning_repo: the false-vs-real deciding detail -------------------------

def test_subdirectory_action_resolves_to_owning_repo():
    """github/codeql-action/init@sha lives in github/codeql-action.

    Querying the three-segment path 404s even for a real commit, so getting this
    wrong reports every CodeQL pin as fake.
    """
    assert verify_pins.owning_repo("github/codeql-action/init") == "github/codeql-action"
    assert verify_pins.owning_repo("github/codeql-action/autobuild") == "github/codeql-action"
    assert verify_pins.owning_repo("github/codeql-action/analyze") == "github/codeql-action"


def test_plain_action_is_unchanged():
    assert verify_pins.owning_repo("actions/checkout") == "actions/checkout"
    assert verify_pins.owning_repo("docker/build-push-action") == "docker/build-push-action"


def test_deeply_nested_path_still_resolves_to_two_segments():
    assert verify_pins.owning_repo("owner/repo/a/b/c") == "owner/repo"


# ---- collect_pins: what counts as a pin -------------------------------------

def _write(tmp_path: Path, body: str, name: str = "wf.yml") -> str:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return str(p)


def test_collects_pinned_refs_with_their_files(tmp_path):
    sha = "b4ffde65f46336ab88eb53be808477a3936bae11"
    a = _write(tmp_path, f"name: A\non: [push]\njobs:\n  j:\n    steps:\n      - uses: actions/checkout@{sha}\n", "a.yml")
    b = _write(tmp_path, f"name: B\non: [push]\njobs:\n  j:\n    steps:\n      - uses: actions/checkout@{sha}\n", "b.yml")
    pins = verify_pins.collect_pins([a, b])
    assert list(pins) == [("actions/checkout", sha)]
    assert pins[("actions/checkout", sha)] == {"a.yml", "b.yml"}


def test_ignores_tag_refs_that_lint_already_flags(tmp_path):
    f = _write(tmp_path, "name: A\non: [push]\njobs:\n  j:\n    steps:\n      - uses: actions/checkout@v4\n")
    assert verify_pins.collect_pins([f]) == {}


def test_ignores_placeholder_refs(tmp_path):
    f = _write(tmp_path, "name: A\non: [push]\njobs:\n  j:\n    steps:\n      - uses: actions/checkout@<pin-latest-sha>\n")
    assert verify_pins.collect_pins([f]) == {}


def test_ignores_short_or_uppercase_hex(tmp_path):
    """A 39-char or uppercase ref is not a pin; it must not be verified as one."""
    for ref in ("actions/checkout@" + "a" * 39, "actions/checkout@" + "A" * 40):
        f = _write(tmp_path, f"name: A\non: [push]\njobs:\n  j:\n    steps:\n      - uses: {ref}\n", "x.yml")
        assert verify_pins.collect_pins([f]) == {}, ref


def test_comments_do_not_break_extraction(tmp_path):
    sha = "ca052bb54ab0790a636c9b5f226502c73d547a25"
    f = _write(tmp_path, f"name: A\non: [push]\njobs:\n  j:\n    steps:\n      - uses: docker/build-push-action@{sha}  # v6\n")
    assert list(verify_pins.collect_pins([f])) == [("docker/build-push-action", sha)]


def test_missing_file_is_skipped_not_crashed(tmp_path):
    assert verify_pins.collect_pins([str(tmp_path / "nope.yml")]) == {}


# ---- the verdict rules ------------------------------------------------------

def test_network_error_is_not_reported_as_fake(tmp_path, monkeypatch):
    """An unreachable GitHub is not evidence about a SHA.

    The distinction decides whether a run points someone at a fabricated pin or
    at a broken network, so a TransportError must not land in the fake bucket.
    """
    sha = "b4ffde65f46336ab88eb53be808477a3936bae11"
    f = _write(tmp_path, f"name: A\non: [push]\njobs:\n  j:\n    steps:\n      - uses: actions/checkout@{sha}\n")

    def boom(action, sha_):
        raise OSError("connection reset")

    # commit_exists catches Exception internally, so simulate its return value
    monkeypatch.setattr(verify_pins, "commit_exists", lambda a, s: (False, "URLError"))
    monkeypatch.setattr(verify_pins.sys, "argv", ["verify-pins.py", f])
    rc = verify_pins.main()
    assert rc == 0, "unverifiable pins must not fail the run"

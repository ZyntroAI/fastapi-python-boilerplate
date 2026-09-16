"""End-to-end: the real failure modes, reproduced and then prevented.

These are the tests that matter most — they encode, as executable checks, the
two behaviours that cost real debugging time on this repository:

1. A CRLF file with no trailing newline passes ``git apply --check`` but fails
   ``git am`` with "patch does not apply", which sends you looking for a content
   conflict that does not exist.
2. Appending through Python text mode normalises CRLF to LF and turns a
   two-line append into a whole-file rewrite.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from patchsuite import append_text, audit_pins, diff_stat, gitops, validate_yaml_file, verify_append


def _format_patch(root: Path, git) -> bytes:
    result = subprocess.run(
        ["git", "format-patch", "-1", "--stdout"], cwd=root, capture_output=True
    )
    return result.stdout


def test_crlf_unterminated_patch_passes_apply_check_but_fails_am(git_sandbox, tmp_path):
    """The headline gotcha, reproduced against real git."""
    root, git = git_sandbox
    wf = root / ".github/workflows/sync.yml"
    wf.parent.mkdir(parents=True)
    base = b"name: Sync\r\n\r\non:\r\n  push:\r\n\r\njobs:\r\n  sync:\r\n    runs-on: ubuntu-latest\r\n    steps:\r\n      - run: echo hi"
    wf.write_bytes(base)  # CRLF, no trailing newline
    git("add", "-A")
    git("commit", "-qm", "base")

    git("checkout", "-qb", "feature")
    wf.write_bytes(base + b"\r\n      - run: echo added\r\n")
    git("add", "-A")
    git("commit", "-qm", "add a step")

    patch = tmp_path / "p.patch"
    patch.write_bytes(_format_patch(root, git))
    git("checkout", "-q", "main")

    # git apply --check is happy ...
    assert gitops.check_patch(patch, root).applies is True

    # ... but git am is not.
    result = gitops.apply_mailbox(patch, root)
    assert result.returncode != 0
    assert "patch does not apply" in (result.stderr + result.stdout)

    diag = gitops.diagnose_patch_failure(result.stderr or result.stdout, result.returncode)
    assert diag.applies is False
    assert diag.likely_cause  # a named cause, not a shrug

    git("am", "--abort")


def test_lf_equivalent_of_the_same_patch_applies_cleanly(git_sandbox, tmp_path):
    """The control: same change, LF endings — git am succeeds."""
    root, git = git_sandbox
    wf = root / ".github/workflows/sync.yml"
    wf.parent.mkdir(parents=True)
    base = b"name: Sync\n\non:\n  push:\n\njobs:\n  sync:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo hi"
    wf.write_bytes(base)
    git("add", "-A")
    git("commit", "-qm", "base")

    git("checkout", "-qb", "feature")
    wf.write_bytes(base + b"\n      - run: echo added\n")
    git("add", "-A")
    git("commit", "-qm", "add a step")

    patch = tmp_path / "p.patch"
    patch.write_bytes(_format_patch(root, git))
    git("checkout", "-q", "main")

    assert gitops.apply_mailbox(patch, root).ok is True


def test_the_audit_predicts_the_failure_before_you_try(git_sandbox):
    """The point of the audit: know which files will break git am, beforehand."""
    root, git = git_sandbox
    wf = root / ".github/workflows"
    wf.mkdir(parents=True)
    (wf / "legacy.yml").write_bytes(b"name: Legacy\r\non: push:")
    (wf / "modern.yml").write_bytes(b"name: Modern\non: push\n")
    git("add", "-A")
    git("commit", "-qm", "base")

    risks = {r.path: r for r in gitops.audit_eol_risk(root)}
    assert risks[".github/workflows/legacy.yml"].at_risk is True
    assert risks[".github/workflows/modern.yml"].at_risk is False


def test_text_mode_roundtrip_blows_up_the_diff_byte_mode_does_not(tmp_path: Path):
    """Why the suite refuses to decode files it writes."""
    target = tmp_path / "CONTRIBUTING.md"
    target.write_bytes(b"# Contributing\r\n\r\nRun the tests.\r\n")

    # Wrong: text-mode read/write normalises CRLF -> LF.
    naive = target.read_text() + "\n## Extra\n"
    target.write_text(naive)
    naive_stat = diff_stat(b"# Contributing\r\n\r\nRun the tests.\r\n", target.read_bytes())
    assert naive_stat["removed"] == 3, "every existing line registers as changed"

    # Right: byte-exact append.
    target.write_bytes(b"# Contributing\r\n\r\nRun the tests.\r\n")
    before = target.read_bytes()
    append_text(target, "## Extra")
    byte_stat = diff_stat(before, target.read_bytes())
    assert byte_stat["removed"] == 0, "nothing existing was touched"
    assert byte_stat["added"] == 1
    assert verify_append(before, target.read_bytes()).ok is True


def test_end_to_end_gate_over_the_broken_fixture(fixtures: Path):
    """Run every check the suite offers over the deliberately-broken project."""
    broken = fixtures / "broken-project"

    # 1. YAML validity — the unquoted colon must be caught, with a location.
    bad_yaml = validate_yaml_file(broken / ".github/workflows/unquoted-colon.yml")
    assert bad_yaml.valid is False
    assert bad_yaml.mark.get("line", 0) > 0

    okay_yaml = validate_yaml_file(broken / ".github/workflows/mixed-refs.yml")
    assert okay_yaml.valid is True

    # 2. Pin audit — unpinned refs found even though the YAML parses.
    pins = audit_pins(broken / ".github/workflows")
    assert pins.compliant is False

    # 3. EOL risk — the CRLF-unterminated file is flagged.
    risks = {r.path for r in gitops.audit_eol_risk(broken) if r.at_risk}
    assert ".github/workflows/crlf-unterminated.yml" in risks


def test_end_to_end_gate_over_the_clean_fixture(fixtures: Path):
    """The clean project must pass everything — no false positives."""
    clean = fixtures / "clean-project"
    for wf in (clean / ".github/workflows").glob("*.yml"):
        assert validate_yaml_file(wf).valid is True
    assert audit_pins(clean / ".github/workflows").compliant is True
    assert all(not r.at_risk for r in gitops.audit_eol_risk(clean))


def test_full_cycle_append_verify_commit(git_sandbox):
    """Append, prove the append, commit — and confirm the diff is only the addition."""
    root, git = git_sandbox
    doc = root / "CONTRIBUTING.md"
    doc.write_bytes(b"# Contributing\r\n\r\nBe kind.\r\n")
    git("add", "-A")
    git("commit", "-qm", "base")

    before = doc.read_bytes()
    append_text(doc, "## Tests\nRun pytest before opening a PR.")
    after = doc.read_bytes()

    assert verify_append(before, after).ok is True

    diff = git("diff", "--numstat").stdout.strip()
    added, removed, _ = diff.split("\t")
    assert removed == "0", "an append must not remove existing lines"
    assert int(added) == 2

    # And the file is still CRLF throughout — no bare LF was introduced by the
    # append on a CRLF target.
    assert b"\n" not in after.replace(b"\r\n", b"")
    assert after.count(b"\r\n") == 5

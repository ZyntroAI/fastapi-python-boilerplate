"""Model tests for the skill's pure decision logic.

These run anywhere — no git, no repo. They pin the three rules that make the
skill safe to run in CI: what counts as a reference, what counts as a
regression, and that a non-canonical file is never silently kept.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pr_triage_automove import classify, config as CFG, probe  # noqa: E402


# --------------------------------------------------------------------------- #
# archive routing
# --------------------------------------------------------------------------- #
def test_every_reference_suffix_has_a_sane_destination():
    layout = CFG.ARCHIVE_LAYOUT
    cases = {
        "old_script.py": "scripts",
        "ci.yml": "manifests",
        "deploy.yaml": "manifests",
        "state.json": "manifests",
        "rows.csv": "exports",
        "log.txt": "exports",
        "fix.patch": "exports",
        "page.html": "html",
        "logo.png": "assets",
        "font.woff2": "assets",
        "bundle.zip": "assets",
        "NOTES.md": "notes",
    }
    for name, expected in cases.items():
        assert classify.dest_for(name, layout, "misc") == expected, name


def test_unknown_extension_falls_back_not_crashes():
    assert classify.dest_for("weird.xyz", CFG.ARCHIVE_LAYOUT, "misc") == "misc"
    assert classify.dest_for("noextension", CFG.ARCHIVE_LAYOUT, "misc") == "misc"


def test_routing_is_case_insensitive():
    assert classify.dest_for("LOGO.PNG", CFG.ARCHIVE_LAYOUT, "misc") == "assets"
    assert classify.dest_for("Readme.MD", CFG.ARCHIVE_LAYOUT, "misc") == "notes"


# --------------------------------------------------------------------------- #
# canonical list
# --------------------------------------------------------------------------- #
def test_canonical_covers_each_ecosystem():
    """A repo adopting this skill should not have to add the obvious basics."""
    c = set(CFG.DEFAULT_CANONICAL)
    for name in ("README.md", "requirements.txt", "pyproject.toml",
                 "package.json", "tsconfig.json", "Dockerfile", "Makefile",
                 ".gitignore", ".env", "main.py", "app.py"):
        assert name in c, f"{name} missing from canonical defaults"


def test_archive_dir_defaults_to_dated_folder():
    assert CFG.archive_dir({}, "2026-09") == "archive/root-2026-09"


def test_archive_dir_honours_override():
    assert CFG.archive_dir({"archive_dir": "_attic"}, "2026-09") == "_attic"


# --------------------------------------------------------------------------- #
# regression rules
# --------------------------------------------------------------------------- #
def test_regression_ranks_ok_high_and_fail_low():
    ok = [{"target": "t", "status": "OK", "signature": "routes=3"}]
    noapp = [{"target": "t", "status": "NO_APP", "signature": "-"}]
    fail = [{"target": "t", "status": "FAIL", "signature": "ImportError: x"}]

    assert probe.regression(ok, fail)          # OK -> FAIL is a regression
    assert probe.regression(noapp, fail)       # NO_APP -> FAIL is a regression
    assert probe.regression(fail, ok) == []    # FAIL -> OK is a fix, not a regression
    assert probe.regression(ok, noapp)         # OK -> NO_APP lost its routes


def test_new_target_appearing_is_not_a_regression():
    """A target that did not exist in the before-run cannot regress anything."""
    before = []
    after = [{"target": "app.main", "status": "FAIL", "signature": "ImportError"}]
    assert probe.regression(before, after) == []


def test_regression_reports_both_signatures_for_the_comment():
    before = [{"target": "app.main", "status": "OK", "signature": "routes=8"}]
    after = [{"target": "app.main", "status": "FAIL", "signature": "ImportError: boom"}]
    reg = probe.regression(before, after)[0]
    assert reg == {"target": "app.main",
                   "before": "OK:routes=8",
                   "after": "FAIL:ImportError: boom"}


def test_no_targets_means_no_regression():
    assert probe.regression([], []) == []


# --------------------------------------------------------------------------- #
# safety defaults
# --------------------------------------------------------------------------- #
def test_max_move_has_a_ceiling_by_default():
    """An unconfigured run must not be able to move an unbounded number of files."""
    assert CFG.load_config(Path("/nonexistent"))["max_move"] > 0


def test_reference_suffixes_include_the_files_that_hide_dependencies():
    suf = tuple(CFG.REFERENCE_SUFFIXES)
    for s in (".md", ".yml", ".yaml", ".json", ".toml", "Makefile"):
        assert s in suf, f"{s} not scanned — a reference would be missed"

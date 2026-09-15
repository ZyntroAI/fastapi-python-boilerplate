"""Tests for the CI workflow linter.

Each case is a real failure mode that occurred in this repository's workflows,
so the suite doubles as the regression list.
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL))

from lint import check  # noqa: E402

EXAMPLES = SKILL / "examples"


def write(tmp_path: Path, body: str, name: str = "wf.yml") -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


GOOD = """
name: X
on:
  pull_request:
    types: [opened]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09
      - run: echo hi
"""


# --------------------------------------------------------------------------- #
# clean input
# --------------------------------------------------------------------------- #
def test_shipped_examples_all_pass():
    """The corrected workflows must be lint-clean — that is their whole point."""
    files = sorted(EXAMPLES.glob("*.yml"))
    assert files, "no examples to check"
    for f in files:
        assert check(f) == [], f"{f.name} failed: {check(f)}"


def test_valid_workflow_passes(tmp_path):
    assert check(write(tmp_path, GOOD)) == []


# --------------------------------------------------------------------------- #
# the six failure modes
# --------------------------------------------------------------------------- #
def test_catches_two_documents_concatenated(tmp_path):
    """The exact bug in the pasted draft: a job key glued to the previous value."""
    bad = GOOD.replace(
        "      - run: echo hi",
        "      - run: echo 'preserved'jobs:\n  b:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo x",
    )
    problems = check(write(tmp_path, bad))
    assert any("YAML" in p for p in problems), problems


def test_catches_tag_pin(tmp_path):
    problems = check(write(tmp_path, GOOD.replace("@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09", "@v4")))
    assert any("not SHA-pinned" in p for p in problems), problems


def test_catches_uses_without_a_ref(tmp_path):
    problems = check(write(tmp_path, GOOD.replace(
        "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09", "actions/checkout")))
    assert any("without a ref" in p for p in problems), problems


def test_catches_short_sha(tmp_path):
    """A truncated SHA is unresolvable and fails at `Set up job`."""
    problems = check(write(tmp_path, GOOD.replace(
        "fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09", "fbc6f399")))
    assert any("not SHA-pinned" in p for p in problems), problems


def test_catches_job_without_runs_on(tmp_path):
    bad = GOOD.replace("    runs-on: ubuntu-latest\n", "")
    problems = check(write(tmp_path, bad))
    assert any("missing runs-on" in p for p in problems), problems


def test_catches_job_without_steps(tmp_path):
    bad = GOOD.replace("    steps:\n      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09\n      - run: echo hi\n", "")
    problems = check(write(tmp_path, bad))
    assert any("missing steps" in p for p in problems), problems


def test_catches_step_with_neither_uses_nor_run(tmp_path):
    bad = GOOD.replace("      - run: echo hi", "      - name: nothing here")
    problems = check(write(tmp_path, bad))
    assert any("neither 'uses' nor 'run'" in p for p in problems), problems


def test_catches_missing_top_level_keys(tmp_path):
    problems = check(write(tmp_path, "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: x\n"))
    assert any("missing required top-level key: name" in p for p in problems), problems
    assert any("missing required top-level key: on" in p for p in problems), problems


def test_catches_hardcoded_aws_key(tmp_path):
    problems = check(write(tmp_path, GOOD.replace("echo hi", "export AKIAIOSFODNN7EXAMPLE")))
    assert any("credential" in p for p in problems), problems


# --------------------------------------------------------------------------- #
# the YAML 1.1 trap
# --------------------------------------------------------------------------- #
def test_bare_on_key_is_not_reported_missing(tmp_path):
    """PyYAML reads `on:` as boolean True. A naive `'on' in doc` check reports
    every valid workflow as broken — which is exactly what happened the first
    time this linter was run against its own examples."""
    assert check(write(tmp_path, GOOD)) == []


def test_quoted_on_key_also_works(tmp_path):
    quoted = GOOD.replace("\non:\n", '\n"on":\n')
    assert check(write(tmp_path, quoted)) == []


# --------------------------------------------------------------------------- #
# non-YAML input must not crash the linter
# --------------------------------------------------------------------------- #
def test_non_mapping_top_level_is_reported(tmp_path):
    problems = check(write(tmp_path, "- just\n- a\n- list\n"))
    assert any("not a mapping" in p for p in problems), problems


def test_empty_file_is_reported(tmp_path):
    problems = check(write(tmp_path, ""))
    assert problems, "an empty file must not pass silently"


def test_unparseable_reports_line_number(tmp_path):
    problems = check(write(tmp_path, "name: X\non: [\n"))
    assert any("YAML" in p for p in problems), problems

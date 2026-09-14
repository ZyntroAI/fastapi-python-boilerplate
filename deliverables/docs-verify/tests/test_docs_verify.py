"""Tests for docs_verify — run against synthetic fixture trees, not the live repo.

Fixtures are built in tmp dirs so the suite is deterministic: it cannot start
failing because an unrelated merge changed a count. The live repo is exercised
separately, by scripts/verify_docs.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from docs_verify import FAIL, PASS, SKIP, verify  # noqa: E402


def build(tmp: Path, *, deliverables=("alpha", "beta"), docs_files=2,
          license_line="Copyright (c) 2026 Example Corp",
          readme_deliverables=2, readme_docs=2, skip_workflows=False,
          workflow_bodies=None) -> Path:
    (tmp / "README.md").write_text(
        f"# T\n\n`deliverables/` holds {readme_deliverables} self-contained suites.\n\n"
        f"`alpha` \u00b7 `beta`\n\n"
        f"| `docs/` | Reference library ({readme_docs} files): things |\n\n"
        f"## Tests\n\n## Deliverables\n\n## License\n",
        encoding="utf-8",
    )
    for name in deliverables:
        (tmp / "deliverables" / name).mkdir(parents=True)
    d = tmp / "docs"
    d.mkdir()
    for i in range(docs_files):
        (d / f"f{i}.md").write_text("x", encoding="utf-8")
    (tmp / "LICENSE").write_text(f"MIT License\n\n{license_line}\n\nPermission\u2026\n",
                                 encoding="utf-8")
    (tmp / "package.json").write_text(json.dumps({"name": "t", "license": "MIT"}),
                                      encoding="utf-8")
    if not skip_workflows:
        wf = tmp / ".github" / "workflows"
        wf.mkdir(parents=True)
        bodies = workflow_bodies or {
            "ci.yml": "name: CI\non: push\njobs:\n  b:\n    steps:\n"
                      "      - uses: actions/checkout@v4\n",
            "ok.yml": "name: OK\non: push\njobs:\n  b:\n    steps:\n"
                      "      - uses: actions/checkout@"
                      "08eba0b27e820071cde6df949e0beb9ba4906955\n",
        }
        for fn, body in bodies.items():
            (wf / fn).write_text(body, encoding="utf-8")
    (tmp / "PROBLEMS.md").write_text(
        "# Problems\n\n## [2026-09-14]\n\n### P-001 \u2014 a\n\n## [2026-09-13]\n\n### P-002 \u2014 b\n",
        encoding="utf-8",
    )
    return tmp


def by_name(report, needle):
    return next(c for c in report.checks if needle in c.name)


def test_clean_tree_passes(tmp_path):
    r = verify(build(tmp_path))
    assert r.passed, [c for c in r.failures]


def test_deliverable_count_drift_is_caught(tmp_path):
    root = build(tmp_path, deliverables=("alpha", "beta", "gamma"), readme_deliverables=2)
    r = verify(root)
    assert not r.passed
    assert by_name(r, "deliverables count").status == FAIL


def test_docs_count_drift_is_caught(tmp_path):
    root = build(tmp_path, docs_files=3, readme_docs=2)
    assert by_name(verify(root), "docs count").status == FAIL


def test_unlisted_deliverable_is_caught(tmp_path):
    root = build(tmp_path, deliverables=("alpha", "beta", "zeta"), readme_deliverables=3)
    c = by_name(verify(root), "names every deliverable")
    assert c.status == FAIL and "zeta" in c.detail


def test_placeholder_license_is_caught(tmp_path):
    root = build(tmp_path, license_line="Copyright (c) 2026 [placeholder]")
    assert by_name(verify(root), "placeholder").status == FAIL


def test_missing_holder_is_caught(tmp_path):
    root = build(tmp_path, license_line="Copyright (c) 2026")
    c = by_name(verify(root), "names a holder")
    assert c.status == FAIL


def test_missing_package_license_is_caught(tmp_path):
    root = build(tmp_path)
    (root / "package.json").write_text(json.dumps({"name": "t"}), encoding="utf-8")
    assert by_name(verify(root), "package.json declares a license").status == FAIL


def test_unparseable_workflow_is_caught(tmp_path):
    root = build(tmp_path, workflow_bodies={
        "broken.yml": "name: x\non: push\njobs: [\n",
    })
    c = by_name(verify(root), "workflows parse")
    assert c.status == FAIL and "broken.yml" in c.detail


def test_pin_measurement_reports_split(tmp_path):
    r = verify(build(tmp_path))
    c = by_name(r, "action pin count")
    assert c.status == PASS and "1/2 pinned" in c.detail


def test_fabricated_draft_heading_is_caught(tmp_path):
    root = build(tmp_path)
    with (root / "README.md").open("a", encoding="utf-8") as f:
        f.write("\n# CI/CD Workflows & Origin Branch Strategy\n")
    assert by_name(verify(root), "fabricated draft").status == FAIL


def test_duplicate_problem_id_is_caught(tmp_path):
    root = build(tmp_path)
    (root / "PROBLEMS.md").write_text(
        "## [2026-09-14]\n\n### P-009 \u2014 a\n\n### P-009 \u2014 b\n", encoding="utf-8")
    c = by_name(verify(root), "problem ids unique")
    assert c.status == FAIL and "P-009" in c.detail


def test_duplicate_date_section_is_caught(tmp_path):
    root = build(tmp_path)
    (root / "PROBLEMS.md").write_text(
        "## [2026-09-14]\n\n### P-001 \u2014 a\n\n## [2026-09-13]\n\n### P-002 \u2014 b\n\n"
        "## [2026-09-14]\n\n### P-003 \u2014 c\n", encoding="utf-8")
    assert by_name(verify(root), "date sections unique").status == FAIL


def test_out_of_order_dates_are_caught(tmp_path):
    root = build(tmp_path)
    (root / "PROBLEMS.md").write_text(
        "## [2026-09-13]\n\n### P-001 \u2014 a\n\n## [2026-09-14]\n\n### P-002 \u2014 b\n",
        encoding="utf-8")
    assert by_name(verify(root), "newest-first").status == FAIL


def test_workflow_section_skipped_without_pyyaml(tmp_path, monkeypatch):
    import builtins
    real_import = builtins.__import__

    def deny(name, *a, **k):
        if name == "yaml":
            raise ImportError("denied")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", deny)
    c = by_name(verify(build(tmp_path)), "workflows parse")
    assert c.status == SKIP


def test_missing_readme_returns_immediately(tmp_path):
    r = verify(tmp_path)
    assert not r.passed
    assert r.checks[0].status == FAIL
    assert len(r.checks) == 1


def test_meta_heading_with_two_ids_is_not_a_duplicate(tmp_path):
    """`### P-001 / P-002 — ...` references two ids; it is not a second P-001."""
    root = build(tmp_path)
    (root / "PROBLEMS.md").write_text(
        "## [2026-09-14]\n\n### P-001 / P-002 \u2014 re-verified \u2014 BLOCKED\n\n"
        "### P-001 \u2014 the real entry \u2014 OPEN\n\n"
        "### P-002 \u2014 another \u2014 OPEN\n", encoding="utf-8")
    assert by_name(verify(root), "problem ids unique").status == PASS


def test_render_lists_every_check(tmp_path):
    from docs_verify import render
    r = verify(build(tmp_path))
    out = render(r)
    for c in r.checks:
        assert c.name in out

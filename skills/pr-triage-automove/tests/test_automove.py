"""Tests for pr-triage-automove — runnable with plain pytest, no fixtures needed.

Everything runs against throwaway git repos in a tmp dir, so the suite proves
the real `git mv` / rollback behaviour rather than a mock of it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]           # skills/pr-triage-automove
# conftest.py registers the `pr_triage_automove` alias for this hyphenated dir.
from pr_triage_automove import automove, classify, config, probe  # noqa: E402


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=True).stdout


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    git(r, "init", "-q")
    git(r, "config", "user.email", "t@example.com")
    git(r, "config", "user.name", "T")
    return r


def commit(repo: Path, msg: str = "c") -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


def write(repo: Path, rel: str, text: str) -> Path:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# --------------------------------------------------------------------------- #
# classify — the AST rule
# --------------------------------------------------------------------------- #
def test_bare_import_from_a_subpackage_protects_the_root_module(repo: Path):
    """Python 3 uses absolute imports, so `import auth` inside app/api/auth.py
    resolves to TOP-LEVEL `auth` — i.e. root auth.py — even though a sibling
    app/api/auth.py exists. The AST rule must therefore KEEP root auth.py.

    A naive implementation that matched on basename would see "auth.py" and
    could get this backwards in either direction; parsing the import graph is
    what makes the answer unambiguous.
    """
    write(repo, "auth.py", "SECRET = 1\n")
    write(repo, "app/__init__.py", "")
    write(repo, "app/api/__init__.py", "")
    write(repo, "app/api/auth.py", "import auth\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    cfg = config.load_config(repo)
    items, _ = classify.classify(repo, cfg, "2026-09")
    rec = {i.path: i for i in items}["auth.py"]

    assert rec.bucket == "keep", "root auth.py is imported — it must not be moved"
    assert "app/api/auth.py" in rec.imported_by


def test_a_self_import_does_not_protect_a_module(repo: Path):
    """`import scratch` inside scratch.py is not a use by anyone else."""
    write(repo, "scratch.py", "import scratch\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    items, _ = classify.classify(repo, config.load_config(repo), "2026-09")
    assert {i.path: i.bucket for i in items}["scratch.py"] == "move"


def test_root_module_actually_imported_is_kept(repo: Path):
    write(repo, "cache.py", "def get(): ...\n")
    write(repo, "app/__init__.py", "")
    write(repo, "app/main.py", "import cache\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    cfg = config.load_config(repo)
    items, _ = classify.classify(repo, cfg, "2026-09")
    rec = {i.path: i for i in items}["cache.py"]

    assert rec.bucket == "keep"
    assert "app/main.py" in rec.imported_by


def test_dotted_import_does_not_count_as_root_use(repo: Path):
    """`from app.services.auth import x` must not protect root auth.py."""
    write(repo, "auth.py", "")
    write(repo, "app/__init__.py", "")
    write(repo, "app/services/__init__.py", "")
    write(repo, "app/services/auth.py", "")
    write(repo, "app/main.py", "from app.services.auth import x\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    items, _ = classify.classify(repo, config.load_config(repo), "2026-09")
    assert {i.path: i for i in items}["auth.py"].bucket == "move"


def test_referenced_file_is_held_not_moved(repo: Path):
    """A manifest naming a root yaml parks it — the gate that saves k8s files."""
    write(repo, "deployment.yaml", "kind: Deployment\n")
    write(repo, "k8s/kustomization.yaml", "resources:\n  - deployment.yaml\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    items, _ = classify.classify(repo, config.load_config(repo), "2026-09")
    rec = {i.path: i for i in items}["deployment.yaml"]

    assert rec.bucket == "hold"
    assert "k8s/kustomization.yaml" in rec.referenced_by


def test_canonical_and_entrypoint_always_kept(repo: Path):
    write(repo, "README.md", "hi\n")
    write(repo, "requirements.txt", "fastapi\n")
    write(repo, "main.py", "app = None\n")
    commit(repo)

    items, _ = classify.classify(repo, config.load_config(repo), "2026-09")
    assert {i.path: i.bucket for i in items} == {
        "README.md": "keep", "requirements.txt": "keep", "main.py": "keep",
    }


def test_unparseable_python_is_reported_not_silently_moved(repo: Path):
    write(repo, "broken.py", "def (:\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    items, meta = classify.classify(repo, config.load_config(repo), "2026-09")
    assert "broken.py" in meta["unparseable_py"]
    # and, being a .py nothing imports, it is still only a *candidate*
    assert {i.path: i.bucket for i in items}["broken.py"] == "move"


def test_dest_for_routes_by_suffix():
    layout = config.ARCHIVE_LAYOUT
    assert classify.dest_for("old.py", layout, "misc") == "scripts"
    assert classify.dest_for("ci.yml", layout, "misc") == "manifests"
    assert classify.dest_for("data.csv", layout, "misc") == "exports"
    assert classify.dest_for("page.html", layout, "misc") == "html"
    assert classify.dest_for("logo.png", layout, "misc") == "assets"
    assert classify.dest_for("notes.md", layout, "misc") == "notes"
    assert classify.dest_for("weird.xyz", layout, "misc") == "misc"


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #
def test_config_overlay_merges(repo: Path):
    write(repo, ".pr-triage-automove.json",
          json.dumps({"max_move": 3, "canonical": ["KEEP.md"]}))
    cfg = config.load_config(repo)
    assert cfg["max_move"] == 3
    assert cfg["canonical"] == ["KEEP.md"]
    assert cfg["archive_layout"]["scripts"] == [".py"]      # default preserved


def test_config_bad_json_falls_back_to_defaults(repo: Path):
    write(repo, ".pr-triage-automove.json", "{not json")
    cfg = config.load_config(repo)
    assert "README.md" in cfg["canonical"]


# --------------------------------------------------------------------------- #
# probe / regression — the safety logic
# --------------------------------------------------------------------------- #
def test_regression_detects_ok_to_fail():
    before = [{"target": "app.main", "status": "OK", "signature": "routes=8"}]
    after = [{"target": "app.main", "status": "FAIL", "signature": "ImportError: x"}]
    regs = probe.regression(before, after)
    assert len(regs) == 1 and regs[0]["target"] == "app.main"


def test_preexisting_failure_is_not_a_regression():
    """A target broken before AND after must not block the move."""
    row = [{"target": "app.core.main", "status": "FAIL", "signature": "ImportError: auth_router"}]
    assert probe.regression(row, row) == []


def test_unknown_is_never_a_regression():
    """Probe could not run — an environment fact, not evidence about the move."""
    before = [{"target": "app.main", "status": "OK", "signature": "routes=8"}]
    after = [{"target": "app.main", "status": "UNKNOWN", "signature": "probe could not run"}]
    assert probe.regression(before, after) == []


def test_improvement_is_not_a_regression():
    before = [{"target": "app.main", "status": "FAIL", "signature": "ImportError: x"}]
    after = [{"target": "app.main", "status": "OK", "signature": "routes=8"}]
    assert probe.regression(before, after) == []


def test_detect_targets_finds_uvicorn_and_vercel(repo: Path):
    write(repo, "Dockerfile", 'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]\n')
    write(repo, "vercel.json", json.dumps({"builds": [{"src": "api/index.py"}]}))
    write(repo, "app/__init__.py", "")
    write(repo, "app/main.py", "app = None\n")
    write(repo, "main.py", "app = None\n")
    found = probe.detect_targets(repo)
    assert "app.main" in found
    assert "main" in found


def test_probe_reports_broken_target_without_crashing(repo: Path):
    write(repo, "bad/main.py", "raise RuntimeError('boom')\n")
    write(repo, "bad/__init__.py", "")
    rows = probe.probe(repo, ["bad.main"])
    assert rows[0]["status"] == "FAIL"
    assert "boom" in rows[0]["signature"]


def test_probe_does_not_leave_its_script_behind(repo: Path):
    write(repo, "ok/__init__.py", "")
    write(repo, "ok/app.py", "class A: routes = []\napp = A()\n")
    probe.probe(repo, ["ok.app"])
    leftovers = list(repo.rglob(".pr-triage-probe.py"))
    assert leftovers == [], "probe script was not cleaned up"


def test_missing_dependency_surfaces_as_a_fail_not_unknown(repo: Path):
    """A target whose deps are absent must FAIL, not pass silently.

    The distinction matters: FAIL before AND after the move is not a regression,
    so the move still proceeds (proven in test_preexisting_failure_is_not_a_regression).
    Reporting it as UNKNOWN would hide a genuinely broken entrypoint.
    """
    write(repo, "needs/pkg/__init__.py", "")
    write(repo, "needs/pkg/main.py", "import definitely_not_installed_xyz\n")
    rows = probe.probe(repo, ["needs.pkg.main"])
    assert rows[0]["status"] == "FAIL"
    assert "definitely_not_installed_xyz" in rows[0]["signature"]


# --------------------------------------------------------------------------- #
# automove — end to end, on a real git repo
# --------------------------------------------------------------------------- #
def test_dry_run_moves_nothing(repo: Path):
    write(repo, "scratch.py", "x = 1\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    rep = automove.run(repo, apply=False, stamp="2026-09")
    assert rep["counts"]["move"] == 1
    assert rep["applied"] is False
    assert (repo / "scratch.py").exists(), "dry-run must not touch the tree"
    assert git(repo, "ls-files").strip().splitlines() == ["README.md", "scratch.py"]


def test_apply_moves_and_keeps_history(repo: Path):
    write(repo, "scratch.py", "x = 1\n")
    write(repo, "export.csv", "a,b\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    rep = automove.run(repo, apply=True, stamp="2026-09")
    assert rep["applied"] is True
    assert not (repo / "scratch.py").exists()
    assert (repo / "archive/root-2026-09/scripts/scratch.py").exists()
    assert (repo / "archive/root-2026-09/exports/export.csv").exists()
    # git sees a rename, not a delete+add
    status = git(repo, "status", "--short")
    assert "R" in status or "renamed" in subprocess.run(
        ["git", "status", "--porcelain", "-M"], cwd=repo,
        capture_output=True, text=True).stdout


def test_rollback_on_import_regression(repo: Path, monkeypatch):
    """If the probe goes backwards, everything is put back."""
    write(repo, "vital.py", "ROUTES = 3\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    # Force the probe to degrade after the move — the move must not stand.
    monkeypatch.setattr(probe, "detect_targets", lambda *a, **k: ["vital"])

    seq = [
        [{"target": "vital", "status": "OK", "signature": "routes=1"}],       # before
        [{"target": "vital", "status": "FAIL", "signature": "ImportError"}],  # after
    ]
    monkeypatch.setattr(probe, "probe", lambda *a, **k: seq.pop(0))

    rep = automove.run(repo, apply=True, stamp="2026-09")
    assert rep["import_health"]["regressions"], "expected a detected regression"
    assert rep.get("rolled_back") is True
    assert (repo / "vital.py").exists(), "rolled back file must be back at root"


def test_max_move_guard_aborts(repo: Path):
    for i in range(4):
        write(repo, f"s{i}.py", "x = 1\n")
    write(repo, "README.md", "hi\n")
    write(repo, ".pr-triage-automove.json", json.dumps({"max_move": 2}))
    commit(repo)

    rep = automove.run(repo, apply=True, stamp="2026-09")
    assert "aborted" in rep
    assert rep["applied"] is False
    assert (repo / "s0.py").exists()


def test_nothing_to_move_is_a_clean_noop(repo: Path):
    write(repo, "README.md", "hi\n")
    write(repo, "main.py", "app = None\n")
    commit(repo)
    rep = automove.run(repo, apply=True, stamp="2026-09")
    assert rep["counts"]["move"] == 0
    assert rep["applied"] is False


def test_comment_renders_official_gate_and_rollback_notice(repo: Path):
    write(repo, "scratch.py", "x = 1\n")
    write(repo, "README.md", "hi\n")
    commit(repo)

    rep = automove.run(repo, apply=False, stamp="2026-09")
    body = automove.render_comment(rep)
    assert "misplaced-file scan" in body
    assert "Import health unchanged" in body
    assert "all three" in body                      # the gate is stated
    assert "`scratch.py`" in body

    rep_bad = dict(rep)
    rep_bad["import_health"] = {
        "before": [], "after": [],
        "regressions": [{"target": "app.main", "before": "OK:routes=8",
                         "after": "FAIL:ImportError"}],
    }
    bad_body = automove.render_comment(rep_bad)
    assert "rolled back" in bad_body


# --------------------------------------------------------------------------- #
# the repo's own tree — the skill must be a no-op on a healthy repo
# --------------------------------------------------------------------------- #
def test_skill_is_idempotent_on_its_own_repo():
    """Second run must find nothing new to move — no drift, no churn."""
    repo_root = ROOT.parents[1]
    if not (repo_root / ".git").is_dir():
        pytest.skip("not inside a git checkout")
    rep1 = automove.run(repo_root, apply=False, stamp="2026-09")
    rep2 = automove.run(repo_root, apply=False, stamp="2026-09")
    assert rep1["counts"]["move"] == rep2["counts"]["move"]

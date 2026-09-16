"""Shared test helpers: paths, a git-sandbox, and result reporting."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SUITE_ROOT = Path(__file__).resolve().parents[1]
SRC = SUITE_ROOT / "src"
FIXTURES = SUITE_ROOT / "fixtures"

sys.path.insert(0, str(SRC))
# Re-assert at position 0 so a coincidentally-installed package of the same
# name cannot shadow the suite under test.
sys.path.remove(str(SRC))
sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def suite_root() -> Path:
    return SUITE_ROOT


@pytest.fixture(scope="session")
def fixtures() -> Path:
    if not FIXTURES.exists():
        subprocess.run(
            [sys.executable, str(SUITE_ROOT / "scripts/make_fixtures.py")], check=True
        )
    return FIXTURES


@pytest.fixture
def clean_file(fixtures: Path, tmp_path: Path) -> Path:
    """A copy of a fixture file, so tests never mutate the fixtures themselves."""
    src = fixtures / "clean-project/notes/CHANGELOG.md"
    dst = tmp_path / "CHANGELOG.md"
    dst.write_bytes(src.read_bytes())
    return dst


@pytest.fixture
def crlf_file(tmp_path: Path) -> Path:
    dst = tmp_path / "crlf.yml"
    dst.write_bytes(b"name: Sync\r\n\r\non:\r\n  push:\r\n")
    return dst


@pytest.fixture
def unterminated_crlf_file(tmp_path: Path) -> Path:
    dst = tmp_path / "unterminated.yml"
    dst.write_bytes(b"name: Sync\r\n\r\non:\r\n  push:")
    return dst


@pytest.fixture
def git_sandbox(tmp_path: Path):
    """A throwaway git repo with an identity configured."""
    root = tmp_path / "sandbox"
    root.mkdir()

    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, check=False
        )

    git("init", "-q", "-b", "main")
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "Test")
    git("config", "commit.gpgsign", "false")
    # An unborn branch reports HEAD; commit once so branch queries are real.
    (root / ".gitkeep").write_text("", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "initial")
    return root, git


def load_report(suite_root: Path) -> dict:
    report = suite_root / "tests" / "report.json"
    return json.loads(report.read_text()) if report.exists() else {}

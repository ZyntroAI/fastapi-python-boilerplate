# tests/test_changed_files.py
import subprocess
import pytest
from detect import changed_files

def test_get_changed_files(monkeypatch):
    # Mock subprocess.run ให้คืนค่าเหมือน git diff
    def mock_run(*args, **kwargs):
        class MockResult:
            stdout = ".github/workflows/build.yml\nREADME.md\n"
        return MockResult()
    
    monkeypatch.setattr(subprocess, "run", mock_run)

    files = changed_files.get_changed_files()
    assert ".github/workflows/build.yml" in files
    assert "README.md" in files

def test_filter_workflow_files():
    files = [
        ".github/workflows/build.yml",
        ".github/workflows/deploy.yaml",
        "README.md",
        "docs/guide.md"
    ]
    workflows = changed_files.filter_workflow_files(files)
    assert len(workflows) == 2
    assert ".github/workflows/build.yml" in workflows
    assert ".github/workflows/deploy.yaml" in workflows

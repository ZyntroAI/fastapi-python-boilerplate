from ..check.installation import validate_permissions

def test_blocks_when_workflow_file_changed_and_no_scope(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN_SCOPES", "contents:write")
    files = [".github/workflows/deploy.yml"]
    result = validate_permissions(files)
    assert result["result"] == "BLOCKED"
    assert result["permission_check"]["workflows"]["granted"] is False

def test_passes_when_only_code_changed(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN_SCOPES", "contents:write")
    files = ["app/main.py"]
    result = validate_permissions(files)
    assert result["result"] == "PASS"

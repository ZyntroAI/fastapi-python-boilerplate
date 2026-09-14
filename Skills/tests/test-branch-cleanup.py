import json
from pathlib import Path

def test_handoff_writes_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from ..handoff_generator import generate_handoff
    result = generate_handoff(
        blocker={"type": "permission"},
        validation={"yaml": True}
    )
    assert Path(".handoff.json").exists()
    assert "BLOCKED" in result["handoff"]["status"]

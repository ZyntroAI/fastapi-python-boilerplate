from ..snapshot import create_snapshot, save_snapshot, load_snapshot

def test_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    snap = create_snapshot("main", "abc123", {}, [], {})
    save_snapshot(snap)
    loaded = load_snapshot()
    assert loaded["commit"] == "abc123"

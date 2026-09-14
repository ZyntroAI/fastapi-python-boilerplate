"""Router-level tests for /obsidian — no live vault, transport injected."""
import json
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import config  # noqa: E402
from app.obsidian import ObsidianClient  # noqa: E402
from app.obsidian.client import Response  # noqa: E402
from app.routers import obsidian as obsidian_router  # noqa: E402


class Recorder:
    def __init__(self, status=200, body="{}"):
        self.calls = []
        self.status = status
        self.body = body

    def __call__(self, method, url, hdrs, raw):
        self.calls.append({"method": method, "url": url, "headers": hdrs, "body": raw})
        return Response(self.status, {}, self.body, (self.body or "").encode())

    @property
    def last(self):
        return self.calls[-1]


@pytest.fixture
def client(monkeypatch):
    """App with the obsidian router mounted and a recording transport."""
    rec = Recorder()
    monkeypatch.setattr(config.settings, "obsidian_api_url", "http://127.0.0.1:27123")
    monkeypatch.setattr(config.settings, "obsidian_allow_write", True)
    monkeypatch.setattr(
        obsidian_router, "_client",
        lambda: ObsidianClient("http://127.0.0.1:27123", "k", transport=rec, allow_write=True),
    )
    app = FastAPI()
    app.include_router(obsidian_router.router)
    return TestClient(app), rec


def test_status_when_connected(client):
    c, _ = client
    r = c.get("/obsidian/status")
    assert r.status_code == 200
    assert r.json() == {"connected": True, "allow_write": True}


def test_status_when_not_connected(monkeypatch):
    monkeypatch.setattr(config.settings, "obsidian_api_url", "")
    app = FastAPI()
    app.include_router(obsidian_router.router)
    c = TestClient(app)
    assert c.get("/obsidian/status").json()["connected"] is False
    r = c.get("/obsidian/tags")
    assert r.status_code == 503
    assert "OBSIDIAN_API_URL" in r.json()["detail"]


def test_list_vault_and_note(client):
    c, rec = client
    rec.body = json.dumps(["A.md", "Notes/"])
    r = c.get("/obsidian/vault")
    assert r.status_code == 200
    assert r.json() == ["A.md", "Notes/"]
    # A markdown read returns the note body verbatim (no Accept negotiation in the recorder).
    rec.body = "# A"
    r = c.get("/obsidian/note", params={"filename": "A.md"})
    assert r.status_code == 200
    assert r.json()["content"] == "# A"


def test_note_meta_returns_frontmatter(client):
    c, rec = client
    rec.body = json.dumps({"content": "x", "frontmatter": {"title": "T"}, "tags": ["t"], "path": "A.md", "stat": {}})
    r = c.get("/obsidian/note", params={"filename": "A.md", "meta": "true"})
    assert r.json()["frontmatter"] == {"title": "T"}


def test_traversal_is_rejected_with_422(client):
    c, _ = client
    r = c.get("/obsidian/note", params={"filename": "../../etc/passwd"})
    assert r.status_code == 422


def test_search_sanitizes_jsonlogic(client):
    c, rec = client
    rec.body = "[]"
    r = c.post("/obsidian/search", json={"query": {"==": [1, 1], "__proto__": {"polluted": True}}})
    assert r.status_code == 200
    sent = json.loads(rec.last["body"].decode())
    assert "__proto__" not in sent


def test_write_requires_auth(client):
    c, _ = client
    r = c.put("/obsidian/note", params={"filename": "A.md"}, json={"content": "x"})
    assert r.status_code == 401


def test_write_rejected_when_flag_off(client, monkeypatch):
    c, rec = client
    monkeypatch.setattr(
        obsidian_router, "_client",
        lambda: ObsidianClient("http://127.0.0.1:27123", "k", transport=rec, allow_write=False),
    )
    token = _token()
    r = c.put(
        "/obsidian/note", params={"filename": "A.md"},
        json={"content": "x"}, headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def _token():
    from app.security import create_access_token
    return create_access_token("tester")


def test_patch_requires_auth_and_validates(client):
    c, rec = client
    token = _token()
    r = c.patch("/obsidian/note", params={"filename": "A.md"}, json={"target_type": "heading", "target": ["A"], "operation": "append"})
    assert r.status_code == 401
    r = c.patch(
        "/obsidian/note", params={"filename": "A.md"},
        json={"target_type": "widget", "target": ["A"], "operation": "append", "content": "x"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422


def test_patch_happy_path_returns_document(client):
    c, rec = client
    rec.body = "# A\n\nx\n"
    token = _token()
    r = c.patch(
        "/obsidian/note", params={"filename": "A.md"},
        json={"target_type": "heading", "target": ["A"], "operation": "append", "content": "x"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["document"].startswith("# A")


def test_delete_and_append_and_open_and_command(client):
    c, rec = client
    token = _token()
    h = {"Authorization": f"Bearer {token}"}
    rec.body = ""
    assert c.post("/obsidian/note/append", params={"filename": "A.md", "target": "Log"}, json={"content": "x"}, headers=h).status_code == 200
    assert rec.last["headers"]["Target"] == "Log"
    assert c.delete("/obsidian/note", params={"filename": "A.md"}, headers=h).status_code == 200
    assert c.post("/obsidian/open", params={"filename": "A.md"}, headers=h).status_code == 200
    assert c.post("/obsidian/commands/editor:toggle-bold/execute", headers=h).status_code == 200


def test_upstream_error_is_translated(client):
    c, rec = client
    rec.status = 404
    rec.body = json.dumps({"message": "not found"})
    r = c.get("/obsidian/note", params={"filename": "missing.md"})
    assert r.status_code == 404

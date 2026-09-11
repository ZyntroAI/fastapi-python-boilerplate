"""Tests for the Obsidian Local REST API client (no live vault needed)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.obsidian import ObsidianClient, ObsidianError, build_patch_instruction  # noqa: E402
from app.obsidian.client import Response  # noqa: E402


class Recorder:
    """Injectable transport that records calls and replays canned responses."""

    def __init__(self, status=200, body="{}", headers=None):
        self.calls = []
        self.status = status
        self.body = body
        self.headers = headers or {}

    def __call__(self, method, url, hdrs, raw):
        self.calls.append({"method": method, "url": url, "headers": hdrs, "body": raw})
        return Response(self.status, self.headers, self.body, (self.body or "").encode())

    @property
    def last(self):
        return self.calls[-1]


def make(**kw):
    rec = Recorder(**kw)
    client = ObsidianClient("http://127.0.0.1:27123", "secret-key", transport=rec, allow_write=True)
    return client, rec


# --- construction / validation --------------------------------------------- #

def test_base_url_scheme_enforced():
    with pytest.raises(ValueError):
        ObsidianClient("ftp://nope", "k")


def test_read_only_blocks_writes():
    client = ObsidianClient("http://127.0.0.1:27123", "k", transport=Recorder())
    with pytest.raises(ObsidianError) as e:
        client.write_note("a.md", "x")
    assert e.value.status == 403


@pytest.mark.parametrize("bad", ["../secrets.md", "/etc/passwd", "a/../../b.md", "nul\x00.md"])
def test_path_traversal_rejected(bad):
    client, _ = make()
    with pytest.raises(ValueError):
        client.read_note(bad)


# --- endpoint coverage ------------------------------------------------------ #

def test_headers_carry_api_key_and_accept():
    client, rec = make()
    client.read_note("Notes/A.md")
    assert rec.last["headers"]["Authorization"] == "Bearer secret-key"
    assert rec.last["method"] == "GET"
    assert rec.last["url"].endswith("/vault/Notes/A.md")


def test_read_note_json_parses_and_sanitizes():
    payload = json.dumps({
        "content": "hi",
        "frontmatter": {"title": "A", "__proto__": {"polluted": True}},
        "tags": ["x"],
        "path": "A.md",
        "stat": {"size": 2},
    })
    client, _ = make(body=payload)
    note = client.read_note_json("A.md")
    assert note.content == "hi"
    assert note.tags == ["x"]
    assert "__proto__" not in note.frontmatter
    assert note.frontmatter["title"] == "A"


def test_document_map_uses_correct_accept():
    client, rec = make(body=json.dumps({"headings": [], "version": "v1"}))
    dm = client.document_map("A.md")
    assert dm["version"] == "v1"
    assert rec.last["headers"]["Accept"] == "application/vnd.olrapi.document-map+json"


def test_list_vault_root_and_dir():
    client, rec = make(body=json.dumps(["a.md"]))
    client.list_vault()
    assert rec.last["url"].endswith("/vault/")
    client.list_dir("Notes")
    assert rec.last["url"].endswith("/vault/Notes/")


def test_search_sends_jsonlogic_and_sanitizes_body():
    client, rec = make(body="[]")
    client.search({"==": [{"var": "frontmatter.done"}, True], "__proto__": {"x": 1}})
    sent = json.loads(rec.last["body"].decode())
    assert "__proto__" not in sent
    assert rec.last["headers"]["Content-Type"] == "application/vnd.olrapi.jsonlogic+json"


def test_simple_search_uses_query_params():
    client, rec = make(body="[]")
    client.simple_search("hello world", context_length=40)
    assert "query=hello+world" in rec.last["url"]
    assert "contextLength=40" in rec.last["url"]


def test_append_with_target_sets_headers():
    client, rec = make(body="")
    client.append_note("A.md", "text", target_type="heading", target="Log")
    assert rec.last["headers"]["Target-Type"] == "heading"
    assert rec.last["headers"]["Target"] == "Log"
    assert rec.last["method"] == "POST"


def test_delete_defaults_to_trash():
    client, rec = make(body="")
    client.delete_note("A.md")
    assert "permanent=false" in rec.last["url"]


def test_patch_note_sends_instruction():
    client, rec = make(body="# A\n")
    client.patch_note("A.md", build_patch_instruction("heading", ["Log"], "append", content="x"))
    sent = json.loads(rec.last["body"].decode())
    assert sent["operation"] == "append"
    assert rec.last["headers"]["Content-Type"].startswith("application/vnd.olrapi.patch-instruction")


def test_api_key_never_leaks_in_error():
    client, _ = make(status=401, body='{"message":"bad key secret-key"}')
    with pytest.raises(ObsidianError) as e:
        client.api_root()
    assert e.value.status == 401


# --- patch instruction algebra --------------------------------------------- #

def test_patch_instruction_requires_exactly_one_payload():
    with pytest.raises(ValueError):
        build_patch_instruction("heading", ["A"], "append")
    with pytest.raises(ValueError):
        build_patch_instruction("heading", ["A"], "append", content="x", value=1)


def test_patch_instruction_rejects_bad_enum():
    with pytest.raises(ValueError):
        build_patch_instruction("widget", ["A"], "append", content="x")
    with pytest.raises(ValueError):
        build_patch_instruction("heading", ["A"], "frobnicate", content="x")


def test_patch_instruction_move_requires_destination():
    with pytest.raises(ValueError):
        build_patch_instruction("heading", ["A"], "replace", scope="parent", content="x")
    ok = build_patch_instruction(
        "heading", ["A"], "replace", scope="parent",
        destination={"parent": ["Appendix"], "place": "last"},
    )
    assert ok["scope"] == "parent" and ok["destination"]["place"] == "last"


def test_patch_instruction_within_cannot_create_target():
    with pytest.raises(ValueError):
        build_patch_instruction("heading", ["A"], "append", content="x", within=-1, create_target_if_missing=True)
    ok = build_patch_instruction("heading", ["A"], "append", content="x", within=-1)
    assert ok["within"] == -1


def test_frontmatter_value_rides_in_value():
    ins = build_patch_instruction("frontmatter", "tags", "append", value=["p/active"], create_target_if_missing=True)
    assert ins["value"] == ["p/active"]
    assert ins["createTargetIfMissing"] is True
    assert "content" not in ins

"""GraphQL + WebSocket client tests — SSRF guard, cache, provenance, flow."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import pytest
from unittest import mock

from skills.fetching.security.ssrf import check_ws as ssrf_check_ws
from skills.fetching.clients.graphql import GraphQLClient
from skills.fetching.clients.websocket import WebSocketClient


# --- WebSocket SSRF guard ---
def test_ssrf_ws_rejects_non_ws_scheme():
    with pytest.raises(ValueError):
        ssrf_check_ws("https://stream.example.com")


def test_ssrf_ws_rejects_private_and_local():
    for u in ("ws://localhost:8000/x", "wss://127.0.0.1/x", "wss://169.254.169.254/x"):
        with pytest.raises(PermissionError):
            ssrf_check_ws(u)


def test_ssrf_ws_allows_public_wss():
    ssrf_check_ws("wss://stream.example.com/socket")  # no raise


# --- GraphQL client ---
async def test_graphql_execute_provenance_and_data():
    gc = GraphQLClient()
    resp = mock.Mock()
    resp.status_code = 200
    resp.json = mock.Mock(return_value={"user": {"id": 1}})
    with mock.patch("httpx.AsyncClient") as MC:
        client = MC.return_value.__aenter__.return_value
        client.post = mock.AsyncMock(return_value=resp)
        out = await gc.execute("https://api.example.com/graphql", "query { user { id } }")
    assert out["data"] == {"user": {"id": 1}}
    assert out["provenance"]["type"] == "graphql"
    assert out["provenance"]["cache"] is None


async def test_graphql_cache_hit():
    gc = GraphQLClient()
    resp = mock.Mock()
    resp.status_code = 200
    resp.json = mock.Mock(return_value={"ok": True})
    calls = {"n": 0}
    async def fake_post(*a, **k):
        calls["n"] += 1
        return resp
    with mock.patch("httpx.AsyncClient") as MC:
        MC.return_value.__aenter__.return_value.post = mock.AsyncMock(side_effect=fake_post)
        first = await gc.execute("https://api.example.com/graphql", "query { ok }", cache_ttl=300)
        second = await gc.execute("https://api.example.com/graphql", "query { ok }", cache_ttl=300)
    assert calls["n"] == 1           # second served from cache
    assert first["provenance"]["cache"] == "MISS"
    assert second["provenance"]["cache"] == "HIT"


async def test_graphql_rejects_http_endpoint():
    gc = GraphQLClient()
    with pytest.raises(ValueError):  # HTTPS-only from ssrf
        await gc.execute("http://api.example.com/graphql", "query { x }")


# --- WebSocket flow (websockets lib mocked) ---
async def test_websocket_connect_send_receive_close():
    wc = WebSocketClient()
    fake_ws = mock.AsyncMock()
    fake_ws.send = mock.AsyncMock()
    fake_ws.close = mock.AsyncMock()
    # receive() yields one message then ends
    async def _agen():
        yield '{"event":"tick"}'
    fake_ws.__aiter__ = mock.Mock(side_effect=lambda: _agen())

    with mock.patch.dict("sys.modules", {"websockets": mock.Mock(connect=mock.AsyncMock(return_value=fake_ws))}):
        conn = await wc.connect("wss://stream.example.com/socket")
        assert conn["status"] == "connected"
        assert conn["provenance"]["type"] == "websocket"

        sent = await wc.send({"action": "subscribe"})
        assert sent["status"] == "sent"

        got = []
        async for m in wc.receive():
            got.append(m)
        assert got[0]["status"] == "message"

        closed = await wc.close()
        assert closed["status"] == "closed"


async def test_websocket_requires_connect_before_send():
    wc = WebSocketClient()
    with pytest.raises(ConnectionError):
        await wc.send("nope")

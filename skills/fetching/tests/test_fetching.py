"""Fetching skill tests — SSRF guard, cache, retry, JSON parse (httpx mocked)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import pytest
from unittest import mock

from skills.fetching.security.ssrf import check as ssrf_check
from skills.fetching.reliability.cache import Cache
from skills.fetching.reliability.retry import retry


# --- SSRF guard ---
def test_ssrf_blocks_non_https():
    with pytest.raises(ValueError):
        ssrf_check("http://example.com")
    with pytest.raises(ValueError):
        ssrf_check("file:///etc/passwd")


def test_ssrf_blocks_private_and_local():
    for u in ("https://localhost/x", "https://127.0.0.1/x", "https://169.254.169.254/latest/meta-data",
              "https://10.0.0.5/x", "https://192.168.1.1/x"):
        with pytest.raises(PermissionError):
            ssrf_check(u)


def test_ssrf_allows_public_https():
    ssrf_check("https://api.github.com/repos/x/y")  # no raise


# --- cache ---
def test_cache_ttl():
    c = Cache(default_ttl=300)
    k = c.key("https://a.example")
    c.set(k, {"x": 1}, ttl=1)
    assert c.get(k) == {"x": 1}
    c.clear()
    assert c.get(k) is None


def test_cache_expired():
    c = Cache(default_ttl=-1)  # already expired
    k = c.key("u")
    c.set(k, "v", ttl=1)
    # set writes with exp = now + ttl (positive); force expiry via short ttl
    import time
    c._store[k]["exp"] = time.time() - 1
    assert c.get(k) is None


# --- retry ---
async def test_retry_succeeds_after_failures():
    calls = {"n": 0}
    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("boom")
        return "ok"
    fn = retry(max_attempts=3, backoff=0)(flaky)
    assert await fn() == "ok"
    assert calls["n"] == 3


async def test_retry_gives_up():
    async def always_fail():
        raise ValueError("nope")
    fn = retry(max_attempts=2, backoff=0)(always_fail)
    with pytest.raises(ValueError):
        await fn()


# --- end-to-end via httpx mock ---
async def test_fetch_url_returns_provenance():
    from skills.fetching import FetchingSkill
    skill = FetchingSkill()
    resp = mock.Mock()
    resp.status_code = 200
    resp.content = b'{"a":1}'
    resp.text = '{"a":1}'
    resp.headers = {"content-type": "application/json"}
    resp.url = "https://api.github.com/x"
    with mock.patch("httpx.AsyncClient") as MC:
        client = MC.return_value.__aenter__.return_value
        client.get = mock.AsyncMock(return_value=resp)
        out = await skill.url("https://api.github.com/x")
    assert out["status"] == 200
    assert "checksum" in out["provenance"]


async def test_fetch_json_parses():
    from skills.fetching import FetchingSkill
    skill = FetchingSkill()
    with mock.patch.object(skill.http, "get", new=mock.AsyncMock(return_value={
        "json": None, "text": '{"k": 42}', "provenance": {}, "status": 200
    })):
        assert await skill.json("https://x.example/a") == {"k": 42}

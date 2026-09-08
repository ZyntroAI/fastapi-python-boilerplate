"""Research skill tests — orchestration, dedup, confidence, SSRF inheritance."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import pytest
from unittest import mock

from skills.research import ResearchSkill


async def _mk_skill(side_effect=None, return_value=None):
    skill = ResearchSkill(fetch=mock.AsyncMock())
    if side_effect is not None:
        skill._fetch.json.side_effect = side_effect
    if return_value is not None:
        skill._fetch.json.return_value = return_value
    return skill


async def test_basic_run_returns_structured():
    skill = await _mk_skill(return_value={"k": 1})
    res = await skill.run("FastAPI", ["https://api.example.com/a"])
    assert "summary" in res and "confidence" in res and "provenance" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert res["sources_used"] == ["https://api.example.com/a"]
    assert res["provenance"]["fetched_by"] == "research"
    assert res["provenance"]["checksum"].startswith("sha256:")


async def test_deduplication():
    skill = await _mk_skill(return_value={"x": 1})
    res = await skill.run("t", ["url1", "url1", "url2"])
    # dedup on: url1 repeated -> skipped
    assert len(res["sources_used"]) == 2
    assert "url1" in res["sources_skipped"]


async def test_confidence_high_when_agree():
    skill = await _mk_skill(return_value={"a": 1})
    res = await skill.run("t", ["https://u1", "https://u2"])
    assert res["confidence"] == 1.0


async def test_confidence_low_on_conflict():
    # different answers -> lower confidence + contradiction flagged
    async def fake(url):
        return {"v": 1} if "u1" in url else {"v": 99}
    skill = await _mk_skill(side_effect=fake)
    res = await skill.run("t", ["https://u1", "https://u2"])
    assert res["confidence"] < 0.7
    assert res["contradictions"]


async def test_ssrf_inherited_skips_internal():
    # fetching raises PermissionError for localhost -> research skips, no usable -> ValueError
    skill = await _mk_skill(side_effect=PermissionError("Blocked host (SSRF)"))
    with pytest.raises(ValueError):
        await skill.run("t", ["http://localhost/x"])


async def test_no_usable_sources_raises():
    skill = await _mk_skill(side_effect=Exception("boom"))
    with pytest.raises(ValueError):
        await skill.run("t", ["https://u1"])


async def test_singleton_importable():
    from skills.research import research as r
    assert hasattr(r, "run")

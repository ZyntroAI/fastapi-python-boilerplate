"""Tests for the cache-reduction toolkit.

Plain pytest, pure stdlib, no fixtures beyond tmp_path — the same shape the
ZyntroAI service tests use. Every test asserts a real behaviour, not a mock.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cache_reduction import (
    analyze_cache_headers,
    audit_redis_info,
    audit_redis_infos,
    diff_headers,
    recompute_after_change,
    scan_path,
    scan_text,
)
from cache_reduction.redis_audit import key_safety_verdict, parse_redis_info


# --------------------------------------------------------------------------
# CR1xx — app-layer cache findings
# --------------------------------------------------------------------------

def test_write_with_ttl_is_clean():
    src = 'await redis.set("user:1", payload, ex=300)\n'
    assert scan_text(src, "app/cache.py") == []


def test_write_without_ttl_is_high():
    src = 'await redis.set("user:1", payload)\n'
    findings = scan_text(src, "app/cache.py")
    assert [f.code for f in findings] == ["CR101"]
    assert findings[0].severity == "high"


def test_sentinel_ttl_zero_is_flagged():
    src = 'await redis.set("user:1", payload, ex=0)\n'
    findings = scan_text(src, "app/cache.py")
    assert [f.code for f in findings] == ["CR102"]


def test_sentinel_ttl_negative_is_flagged():
    src = 'redis.setex("session:9", -1, blob)\n'
    findings = scan_text(src, "app/cache.py")
    assert [f.code for f in findings] == ["CR102"]


def test_real_setex_ttl_is_clean():
    src = 'redis.setex("session:9", 900, blob)\n'
    assert scan_text(src, "app/cache.py") == []


def test_unbounded_memoization_is_flagged():
    src = "@cache\ndef load_config(path):\n    return _read(path)\n"
    findings = scan_text(src, "app/config.py")
    assert [f.code for f in findings] == ["CR103"]


def test_bounded_memoization_is_clean():
    src = "@lru_cache(maxsize=128)\ndef load_config(path):\n    return _read(path)\n"
    assert scan_text(src, "app/config.py") == []


def test_wildcard_delete_is_flagged():
    src = 'for k in redis.keys("user:*"):\n    redis.delete(k)\n'
    findings = scan_text(src, "app/cache.py")
    assert "CR104" in [f.code for f in findings]


def test_full_flush_is_high():
    src = "redis.flushdb()\n"
    findings = scan_text(src, "app/cache.py")
    assert [f.code for f in findings] == ["CR105"]
    assert findings[0].severity == "high"


# --------------------------------------------------------------------------
# CR2xx — agent-context findings
# --------------------------------------------------------------------------

def test_oversized_prompt_file_is_flagged():
    text = "---\ntype: skill\n---\n\n# Big\n\n" + ("filler line\n" * 4000)
    codes = [f.code for f in scan_text(text, "skills/big.md")]
    assert "CR201" in codes


def test_duplicate_block_is_flagged_once():
    block = "## Section\n\n" + ("identical content here\n" * 20)
    text = f"# Note\n\n{block}\n\n{block}\n"
    findings = [f for f in scan_text(text, "skills/dup.md") if f.code == "CR202"]
    assert len(findings) == 1


def test_inlined_urls_are_low():
    text = "# Note\n\nSee https://example.com/a and https://example.com/b\n"
    findings = [f for f in scan_text(text, "skills/urls.md") if f.code == "CR203"]
    assert findings and findings[0].severity == "low"


# --------------------------------------------------------------------------
# scan_path
# --------------------------------------------------------------------------

def test_scan_path_skips_vendor_dirs(tmp_path: Path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "cache.py").write_text('await redis.set("a", 1)\n')
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dep.js").write_text('cache.set("b", 1)\n')

    report = scan_path(tmp_path)
    assert report.files_scanned == 1
    assert all("node_modules" not in f.path for f in report.findings)


def test_scan_path_missing_root_is_empty_report():
    report = scan_path("/nonexistent/path/for/test")
    assert report.files_scanned == 0
    assert report.findings == []
    assert report.grade == "A"


def test_report_score_and_grade_track_severity(tmp_path: Path):
    (tmp_path / "a.py").write_text("redis.flushdb()\n")
    report = scan_path(tmp_path)
    assert report.score == 5
    assert report.grade == "C"

    (tmp_path / "b.py").write_text('await redis.set("k", 1)\n')
    report = scan_path(tmp_path)
    assert report.score == 10
    assert report.grade == "D"


def test_report_is_json_serialisable():
    report = scan_path("/nonexistent")
    assert json.loads(json.dumps(report.to_dict()))["grade"] == "A"


# --------------------------------------------------------------------------
# headers
# --------------------------------------------------------------------------

def test_cacheable_with_max_age():
    r = analyze_cache_headers("Cache-Control: public, max-age=300")
    assert r["cacheable"] is True
    assert r["directives"]["max-age"] == "300"


def test_missing_header_is_high():
    r = analyze_cache_headers("Content-Type: text/html")
    assert r["cacheable"] is False
    assert [f["code"] for f in r["findings"]] == ["H101"]


def test_bare_public_flags_shared_lifetime():
    r = analyze_cache_headers("Cache-Control: public")
    assert r["cacheable"] is False
    assert "H102" in [f["code"] for f in r["findings"]]


def test_public_with_s_maxage_is_clean():
    r = analyze_cache_headers("Cache-Control: public, max-age=60, s-maxage=600")
    assert r["cacheable"] is True
    assert r["findings"] == []


def test_private_with_s_maxage_is_contradictory():
    r = analyze_cache_headers("Cache-Control: private, max-age=60, s-maxage=600")
    assert "H103" in [f["code"] for f in r["findings"]]


def test_no_store_is_not_cacheable():
    r = analyze_cache_headers("Cache-Control: no-store, max-age=3600")
    assert r["cacheable"] is False
    assert "H106" in [f["code"] for f in r["findings"]]


def test_no_store_alone_is_clean():
    r = analyze_cache_headers("Cache-Control: no-store")
    assert r["cacheable"] is False
    assert r["findings"] == []


def test_parse_handles_quoted_and_spaced_directives():
    r = analyze_cache_headers('Cache-Control: public , max-age="600"')
    assert r["directives"]["max-age"] == "600"
    assert r["cacheable"] is True


def test_headers_accept_a_mapping():
    r = analyze_cache_headers({"Cache-Control": "public, max-age=120"})
    assert r["cacheable"] is True


def test_stale_after_change_when_url_and_headers_unchanged():
    before = "Cache-Control: public, max-age=31536000"
    after = "Cache-Control: public, max-age=31536000"
    r = analyze_cache_headers(before, after)
    assert r["stale_after_change"] is True
    assert "H105" in [f["code"] for f in r["findings"]]


def test_etag_prevents_stale_after_change():
    before = "Cache-Control: public, max-age=60\nETag: \"v1\""
    after = "Cache-Control: public, max-age=60\nETag: \"v2\""
    r = analyze_cache_headers(before, after)
    assert r["stale_after_change"] is False


def test_changed_lifetime_prevents_stale_after_change():
    r = analyze_cache_headers(
        "Cache-Control: public, max-age=300",
        "Cache-Control: public, max-age=60",
    )
    assert r["stale_after_change"] is False
    assert r["changed_directives"] == ["max-age"]


def test_diff_headers_reports_changes():
    d = diff_headers(
        "Cache-Control: public, max-age=300\nETag: \"a\"",
        "Cache-Control: private, max-age=0\nETag: \"b\"",
    )
    assert "max-age" in d["changed_directives"]
    assert d["etag_changed"] is True
    assert d["cacheable_before"] is True
    assert d["cacheable_after"] is False


def test_recompute_confirms_the_change_landed():
    r = analyze_cache_headers(
        "Cache-Control: public, max-age=31536000",
        "Cache-Control: public, max-age=31536000",
    )
    out = recompute_after_change(r)
    assert out["rechecked"] is True
    assert out["was_stale"] is True
    assert out["still_stale"] is True


def test_recompute_without_update_is_explicit():
    r = analyze_cache_headers("Cache-Control: public, max-age=60")
    assert recompute_after_change(r) == {
        "rechecked": False, "reason": "no updated response was supplied",
    }


# --------------------------------------------------------------------------
# redis
# --------------------------------------------------------------------------

HEALTHY_INFO = """\
# Memory
used_memory:104857600
used_memory_human:100.00M
maxmemory:268435456
maxmemory_human:256.00M
maxmemory_policy:volatile-ttl
mem_fragmentation_ratio:1.10

# Stats
keyspace_hits:900000
keyspace_misses:100000
evicted_keys:0
expired_keys:4200

# Keyspace
db0:keys=50000,expires=45000,avg_ttl=900000
"""

PRESSURE_INFO = """\
# Memory
used_memory:1073741824
used_memory_human:1.00G
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
mem_fragmentation_ratio:2.40

# Stats
keyspace_hits:200000
keyspace_misses:800000
evicted_keys:15000
expired_keys:10

# Keyspace
db0:keys=200000,expires=5000,avg_ttl=0
"""


def test_parse_redis_info_sections():
    sections = parse_redis_info(HEALTHY_INFO)
    assert sections["memory"]["maxmemory_policy"] == "volatile-ttl"
    assert sections["stats"]["keyspace_hits"] == "900000"


def test_healthy_instance_has_no_findings():
    r = audit_redis_info(HEALTHY_INFO)
    assert r["findings"] == []
    assert r["hit_rate"] == pytest.approx(0.9)
    assert r["ttl_coverage"] == pytest.approx(0.9)


def test_pressure_instance_flags_every_problem():
    r = audit_redis_info(PRESSURE_INFO)
    codes = {f["code"] for f in r["findings"]}
    assert {"R101", "R102", "R104", "R105", "R106"} <= codes
    # R103 (noeviction once full) is correctly suppressed here: with
    # maxmemory=0 the store never fills, so R102 is the live finding.
    assert "R103" not in codes


def test_noeviction_with_a_limit_is_flagged():
    info = PRESSURE_INFO.replace("maxmemory:0", "maxmemory:268435456")
    r = audit_redis_info(info)
    assert "R103" in {f["code"] for f in r["findings"]}


def test_hit_rate_low_is_high_severity():
    r = audit_redis_info(PRESSURE_INFO)
    hit = next(f for f in r["findings"] if f["code"] == "R105")
    assert hit["severity"] == "high"


def test_reclaimable_estimate_tracks_missing_ttls():
    r = audit_redis_info(PRESSURE_INFO)
    # 1 GiB used, only 2.5% of keys carry a TTL -> most of the dataset is reclaimable.
    assert r["reclaimable_bytes"] > 1_000_000_000
    assert r["reclaimable_human"].endswith("GB") or r["reclaimable_human"].endswith("MB")


def test_missing_maxmemory_is_flagged():
    r = audit_redis_info(PRESSURE_INFO)
    assert "R102" in {f["code"] for f in r["findings"]}


def test_key_safety_verdict_matches_production_stance():
    assert "fail-open" in key_safety_verdict(True)
    assert "fail-closed" in key_safety_verdict(False)
    assert "fail-open" in audit_redis_info(HEALTHY_INFO, fail_open=True)["key_safety"]


def test_fleet_totals_sum_instances():
    out = audit_redis_infos([("cache-a", HEALTHY_INFO), ("cache-b", PRESSURE_INFO)])
    assert len(out["instances"]) == 2
    assert out["total_used_bytes"] == pytest.approx(104857600 + 1073741824)


def test_flat_info_without_sections_still_parses():
    flat = "used_memory:1000\nkeyspace_hits:9\nkeyspace_misses:1\n"
    r = audit_redis_info(flat)
    assert r["used_memory"] == 1000
    assert r["hit_rate"] == pytest.approx(0.9)

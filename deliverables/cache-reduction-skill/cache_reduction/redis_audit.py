"""Redis INFO analysis — where the memory is going and whether the cache works.

Takes pasted ``INFO`` output (never a live connection) and returns the numbers
that matter for a cache-reduction pass, plus verdicts for memory pressure,
hit-rate, eviction, and how much of the keyspace could be reclaimed.

Also honours the ZyntroAI production stance: a cache that cannot answer must
degrade, not fail. ``key_safety_verdict`` reports whether a Redis outage would
take the service down.
"""

from __future__ import annotations

import re
from typing import Iterable

__all__ = ["parse_redis_info", "audit_redis_info", "audit_redis_infos", "key_safety_verdict"]

_SECTION = re.compile(r"^#\s*(\w+)\s*$", re.M)
_KV = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):([^\r\n]*)$", re.M)
_KEYS_DB = re.compile(r"^db(\d+):keys=(\d+),expires=(\d+)(?:,avg_ttl=(\d+))?", re.M)


def parse_redis_info(text: str) -> dict:
    """Split Redis ``INFO`` output into sections of key/value pairs."""
    sections: dict[str, dict[str, str]] = {}
    marks = [(m.start(), m.group(1).lower()) for m in _SECTION.finditer(text)]
    for idx, (pos, name) in enumerate(marks):
        end = marks[idx + 1][0] if idx + 1 < len(marks) else len(text)
        body = text[pos:end]
        body = body.split("\n", 1)[1] if "\n" in body else ""
        sections[name] = {k: v.strip() for k, v in _KV.findall(body)}
    if not sections:  # bare key:value dump with no section headers
        sections["_flat"] = {k: v.strip() for k, v in _KV.findall(text)}
    return sections


def _flatten(sections: dict) -> dict[str, str]:
    flat: dict[str, str] = {}
    for body in sections.values():
        flat.update(body)
    return flat


def _num(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(str(value).strip())
    except ValueError:
        return default


def _human(num_bytes: float) -> str:
    step = 1024.0
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < step or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= step
    return f"{value:.1f} TB"


def key_safety_verdict(fail_open: bool) -> str:
    """State plainly whether a Redis outage degrades or crashes the service."""
    if fail_open:
        return ("fail-open — a Redis outage degrades to cache misses rather than "
                "taking the service down")
    return ("fail-closed — a Redis outage is a service outage; move cache reads "
            "behind a try/except that returns a miss")


def audit_redis_info(text: str, name: str = "default", fail_open: bool = True) -> dict:
    """Audit one Redis ``INFO`` dump.

    Reports memory pressure, hit rate, eviction policy, keyspace TTL coverage,
    and a byte estimate of what a TTL pass could reclaim.
    """
    sections = parse_redis_info(text)
    flat = _flatten(sections)
    # A bare key:value dump has no section headers — fall back to the flat map
    # so a pasted excerpt still audits identically to full INFO output.
    memory = {**flat, **sections.get("memory", {})}
    stats = {**flat, **sections.get("stats", {})}
    keyspace = {**flat, **sections.get("keyspace", {})}

    used = _num(memory.get("used_memory"))
    maxmemory = _num(memory.get("maxmemory"))
    policy = memory.get("maxmemory_policy", "unknown") or "unknown"
    frag = _num(memory.get("mem_fragmentation_ratio"))

    hits = _num(stats.get("keyspace_hits"))
    misses = _num(stats.get("keyspace_misses"))
    evicted = _num(stats.get("evicted_keys"))
    expired = _num(stats.get("expired_keys"))
    total_lookups = hits + misses
    hit_rate = (hits / total_lookups) if total_lookups else None

    keys = expires = 0
    for _, k, e, *_ in _KEYS_DB.findall(text):
        keys += int(k)
        expires += int(e)
    ttl_ratio = (expires / keys) if keys else None

    findings: list[dict] = []

    def add(code: str, severity: str, message: str) -> None:
        findings.append({"code": code, "severity": severity, "message": message})

    if frag:
        if frag >= 2.0:
            add("R101", "high",
                f"Fragmentation {frag:.2f} — RSS is roughly {frag:.1f}x the "
                "dataset; a restart or MEMORY PURGE reclaims the gap.")
        elif frag >= 1.5:
            add("R101", "medium",
                f"Fragmentation {frag:.2f} — moderate overhead above the dataset.")

    if maxmemory <= 0:
        add("R102", "high",
            "No maxmemory set — the cache can grow until the host runs out of "
            "memory. Set maxmemory and a matching eviction policy.")
    if policy in ("noeviction", "unknown") and maxmemory > 0:
        add("R103", "high",
            f"maxmemory_policy is '{policy}' — once full, writes fail instead of "
            "reclaiming. Use volatile-ttl or allkeys-lru.")

    if evicted > 0:
        add("R104", "high",
            f"{int(evicted):,} keys evicted — the working set does not fit. Cut "
            "lifetimes or shard before raising memory.")

    if hit_rate is not None:
        if hit_rate < 0.70:
            add("R105", "high",
                f"Hit rate {hit_rate:.1%} — most lookups miss, so the cache costs "
                "memory without saving work. Check key shape and TTLs.")
        elif hit_rate < 0.85:
            add("R105", "medium",
                f"Hit rate {hit_rate:.1%} — below the 85% healthy line.")

    if ttl_ratio is not None and ttl_ratio < 0.10:
        add("R106", "medium",
            f"Only {ttl_ratio:.1%} of keys carry a TTL — the rest never expire "
            "on their own and are the main reclaimable pool.")

    reclaimable = used * (1 - ttl_ratio) if (used and ttl_ratio is not None) else 0.0

    return {
        "name": name,
        "used_memory": used,
        "used_memory_human": memory.get("used_memory_human") or _human(used),
        "maxmemory": maxmemory,
        "maxmemory_human": memory.get("maxmemory_human") or (_human(maxmemory) if maxmemory else "unset"),
        "maxmemory_policy": policy,
        "fragmentation_ratio": frag,
        "keyspace_hits": hits,
        "keyspace_misses": misses,
        "hit_rate": hit_rate,
        "evicted_keys": evicted,
        "expired_keys": expired,
        "total_keys": keys,
        "keys_with_ttl": expires,
        "ttl_coverage": ttl_ratio,
        "reclaimable_bytes": reclaimable,
        "reclaimable_human": _human(reclaimable) if reclaimable else "0 B",
        "key_safety": key_safety_verdict(fail_open),
        "findings": findings,
        "raw_keys": flat.get("_flat", {}),
    }


def audit_redis_infos(
    instances: Iterable[tuple[str, str]], fail_open: bool = True
) -> dict:
    """Audit several ``(name, info_text)`` dumps and total the fleet."""
    results = [audit_redis_info(text, name=n, fail_open=fail_open) for n, text in instances]
    return {
        "instances": results,
        "total_used_bytes": sum(r["used_memory"] for r in results),
        "total_used_human": _human(sum(r["used_memory"] for r in results)),
        "total_reclaimable_bytes": sum(r["reclaimable_bytes"] for r in results),
        "total_reclaimable_human": _human(sum(r["reclaimable_bytes"] for r in results)),
        "total_findings": sum(len(r["findings"]) for r in results),
    }

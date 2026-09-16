"""HTTP / CDN Cache-Control analysis.

Answers the three questions that decide whether a response is wasting browser
and edge cache: may it be stored at all, for how long, and does the freshness
lifetime still match the asset's content? Also gives you the cache-bust check —
after a deploy, would a returning client still be served the old bytes?
"""

from __future__ import annotations

import re
from typing import Mapping

__all__ = [
    "parse_headers",
    "parse_cache_control",
    "analyze_cache_headers",
    "diff_headers",
    "recompute_after_change",
]

_HEADER_LINE = re.compile(r"^([A-Za-z0-9!#$%&'*+\-.^_`|~]+)\s*:\s*(.*)$")

_K, _S = "key", "severity"


def parse_headers(raw: str | Mapping[str, str]) -> dict[str, str]:
    """Normalise either a raw header block or a mapping to lower-cased keys."""
    if hasattr(raw, "items"):
        return {str(k).lower(): str(v) for k, v in raw.items()}  # type: ignore[union-attr]
    out: dict[str, str] = {}
    for line in str(raw).splitlines():
        if not line.strip() or line.lower().startswith("http/"):
            continue
        m = _HEADER_LINE.match(line)
        if m:
            out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def parse_cache_control(value: str) -> dict[str, object]:
    """Parse a Cache-Control value into ``{directive: value_or_True}``.

    Handles quoted values, whitespace after commas, and yes/no style argument
    forms (``public``, ``no-store``) alongside number forms
    (``max-age=300``, ``s-maxage="600"``).
    """
    directives: dict[str, object] = {}
    pending: str | None = None
    for token in (t.strip() for t in str(value).split(",")):
        if not token:
            continue
        if "=" in token:
            name, val = token.split("=", 1)
            name = name.strip().lower()
            val = val.strip().strip('"')
            if pending is not None:
                directives[pending] = True
                pending = None
            directives[name] = val
        else:
            if pending is not None:
                directives[pending] = True
            pending = token.lower()
    if pending is not None:
        directives[pending] = True
    return directives


def _as_int(directives: Mapping[str, object], key: str) -> int | None:
    if key not in directives:
        return None
    try:
        return int(str(directives[key]).strip())
    except (TypeError, ValueError):
        return None


def analyze_cache_headers(
    original_raw: str | Mapping[str, str],
    updated_raw: str | Mapping[str, str] | None = None,
) -> dict:
    """Analyse one response, optionally against the headers of its new build.

    Pass ``updated_raw`` when a deploy changes the asset but not the URL —
    the result then tells you whether the change would actually reach clients.
    """
    headers = parse_headers(original_raw)
    cc_raw = headers.get("cache-control", "").strip()
    directives = parse_cache_control(cc_raw) if cc_raw else {}
    etag = headers.get("etag", "")

    max_age = _as_int(directives, "max-age")
    s_max_age = _as_int(directives, "s-maxage")
    immutable = "immutable" in directives
    public = "public" in directives
    private = "private" in directives
    no_store = "no-store" in directives

    if no_store:
        cacheable, reason = False, "Cache-Control: no-store"
    elif max_age is None and s_max_age is None:
        cacheable, reason = False, "no freshness lifetime declared"
    elif max_age == 0 and (s_max_age is None or s_max_age == 0):
        cacheable, reason = False, "max-age=0"
    else:
        cacheable, reason = True, "explicit freshness lifetime"

    findings: list[dict] = []

    def add(severity: str, message: str, code: str) -> None:
        findings.append({"code": code, "severity": severity, "message": message})

    if not cc_raw:
        add("high", "No Cache-Control header — the client falls back to "
                    "heuristic freshness and may keep stale bytes.",
            "H101")
    if public and s_max_age is None:
        add("medium", "Bare 'public' shares the response with every cache but "
                      "sets no shared lifetime — 'public, s-maxage=N' is the "
                      "explicit form.", "H102")
    if private and s_max_age is not None:
        add("high", "'private' and 's-maxage' together are contradictory — the "
                    "shared lifetime is dead config.", "H103")
    if cacheable and max_age is None and s_max_age is not None:
        add("low", "Shared-only lifetime: intermediaries cache this, clients do "
                   "not re-validate cheaply. Add max-age if browsers should "
                   "hold it too.", "H104")
    if no_store and (max_age is not None or s_max_age is not None):
        add("medium", "no-store alongside a freshness lifetime — no-store wins, "
                      "so the max-age values are misleading.", "H106")
    if cacheable and not immutable and max_age is not None and max_age >= 31_536_000:
        add("low", "Very long max-age without 'immutable' — revalidation "
                   "requests will still fire.", "H107")

    result: dict = {
        "headers": headers,
        "cache_control_raw": cc_raw,
        "directives": directives,
        "etag": etag,
        "max_age": max_age,
        "s_max_age": s_max_age,
        "immutable": immutable,
        "cacheable": cacheable,
        "cacheable_reason": reason,
        "findings": findings,
    }

    if updated_raw is not None:
        updated = analyze_cache_headers(updated_raw)
        differing = sorted(
            k for k in set(directives) | set(updated["directives"])
            if directives.get(k) != updated["directives"].get(k)
        )
        stale = (
            result["cacheable"]
            and updated["cacheable"]
            and directives == updated["directives"]
            and not etag
        )
        if stale:
            add("high", "Asset content changed but the URL and Cache-Control are "
                        "unchanged with no ETag — returning clients keep the old "
                        "bytes until the lifetime expires. Add a content hash to "
                        "the filename or shorten the lifetime.", "H105")
        result["updated"] = updated
        result["changed_directives"] = differing
        result["stale_after_change"] = stale

    return result


def diff_headers(before: str | Mapping[str, str],
                 after: str | Mapping[str, str]) -> dict:
    """Compare the cache-relevant headers of two responses."""
    a = analyze_cache_headers(before)
    b = analyze_cache_headers(after)
    changed = sorted(
        k for k in set(a["directives"]) | set(b["directives"])
        if a["directives"].get(k) != b["directives"].get(k)
    )
    return {
        "before": a["directives"],
        "after": b["directives"],
        "changed_directives": changed,
        "cacheable_before": a["cacheable"],
        "cacheable_after": b["cacheable"],
        "etag_before": a["etag"],
        "etag_after": b["etag"],
        "etag_changed": a["etag"] != b["etag"],
    }


def recompute_after_change(result: dict) -> dict:
    """Re-run the analysis once the deploy has landed.

    ``result`` is the output of :func:`analyze_cache_headers` called *with*
    ``updated_raw``. Returns the fresh analysis plus whether the earlier
    stale-after-change warning was real.
    """
    updated = result.get("updated")
    if not updated:
        return {"rechecked": False, "reason": "no updated response was supplied"}

    # updated_capture holds the raw directive string, not a header block —
    # re-wrap it so the analyser sees a real Cache-Control header.
    fresh_raw = updated.get("cache_control_raw", "")
    fresh = analyze_cache_headers({"cache-control": fresh_raw} if fresh_raw else {})
    return {
        "rechecked": True,
        "was_stale": bool(result.get("stale_after_change")),
        "still_stale": fresh["cacheable"] and not fresh["etag"],
        "fresh": fresh,
    }

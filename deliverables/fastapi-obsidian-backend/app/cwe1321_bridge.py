"""CWE-1321 sanitizer bridge (Python) for the Obsidian integration.

Vendored, dependency-free mirror of
``deliverables/cwe1321-protection-suite/python/safe_parser.py`` so this
backend can import the guard without reaching outside its own package. The
logic is kept identical to the suite's Python layer; only the names differ
(``sanitize_prototype_keys`` is the suite's ``strip_blocked_keys``) so both
sides of the TypeScript/Python pair read naturally in their own environment.

Who it guards: every untrusted payload that crosses the Obsidian boundary —
request bodies, search queries, and the JSON the vault returns.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

# Keys that frameworks may map onto object / class state.
BLOCKED_KEYS: frozenset = frozenset(("__proto__", "prototype", "constructor"))


def is_blocked_key(key: Any) -> bool:
    """True when ``key`` is unsafe to copy onto an object / class boundary."""
    return isinstance(key, str) and key in BLOCKED_KEYS


def sanitize_prototype_keys(obj: Any) -> Any:
    """Recursively drop blocked keys from untrusted dict/list input.

    Returns a structurally identical, pollution-free copy.
    """
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            if is_blocked_key(k):
                continue
            out[k] = sanitize_prototype_keys(v)
        return out
    if isinstance(obj, list):
        return [sanitize_prototype_keys(item) for item in obj]
    return obj


def safe_update_dict(
    target: Dict[str, Any],
    source: Dict[str, Any],
    *,
    drop: bool = True,
) -> Dict[str, Any]:
    """Update ``target`` from untrusted ``source`` without blocked keys."""
    for k, v in source.items():
        if is_blocked_key(k):
            if not drop:
                raise ValueError(f"blocked prototype-polluting key: {k!r}")
            continue
        target[k] = sanitize_prototype_keys(v)
    return target


def report(
    *,
    status: str = "ok",
    keys: Optional[list] = None,
    remediation: str = "",
) -> Dict[str, Any]:
    """Standard remediation-report shape shared across the suite."""
    return {"status": status, "keys": keys or [], "remediation": remediation}


__all__ = [
    "BLOCKED_KEYS",
    "is_blocked_key",
    "sanitize_prototype_keys",
    "safe_update_dict",
    "report",
]

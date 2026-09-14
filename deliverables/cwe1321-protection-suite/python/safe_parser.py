"""
safe_parser.py — CWE-1321 Prototype Pollution safe loaders (Python).

Pure-stdlib runtime remediation for the Python layer. Detection rules
(Bandit config + Semgrep) flag risky assignment/merge; these helpers load and
update untrusted dicts while refusing keys that would pollute class /
attribute state (`__proto__`, `prototype`, `constructor`).

Python dicts are not vulnerable to `Object.prototype` pollution the way JS is,
but frameworks that map dict keys onto objects / attributes (FastAPI/Pydantic
coercion, ORM `**kwargs`, `setattr` marshalling) can be — so we strip the
reserved keys at the boundary and provide a FastAPI/Pydantic-safe loader.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

# Keys that frameworks may map onto object/class state. ``__proto__`` and
# ``prototype`` are the classic polluters; ``constructor`` enables
# constructor/prototype confusion in JS-derived flows.
BLOCKED_KEYS: frozenset = frozenset(("__proto__", "prototype", "constructor"))


def is_blocked_key(key: Any) -> bool:
    """True when ``key`` is unsafe to copy onto an object / class boundary."""
    return isinstance(key, str) and key in BLOCKED_KEYS


def strip_blocked_keys(obj: Any) -> Any:
    """Recursively drop blocked keys from untrusted dict/list input.

    Returns a structurally identical, pollution-free copy.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if is_blocked_key(k):
                continue
            out[k] = strip_blocked_keys(v)
        return out
    if isinstance(obj, list):
        return [strip_blocked_keys(item) for item in obj]
    return obj


def safe_load_json(
    text: str, *, strip: bool = True, **kwargs: Any
) -> Dict[str, Any]:
    """``json.loads`` that strips prototype-polluting keys at the boundary.

    Passed straight through to ``json.loads`` for everything else.
    """
    data = json.loads(text, **kwargs)
    if strip:
        data = strip_blocked_keys(data)
    return data


def safe_update_dict(
    target: Dict[str, Any],
    source: Dict[str, Any],
    *,
    drop: bool = True,
) -> Dict[str, Any]:
    """Update ``target`` from an untrusted ``source`` without blocked keys.

    ``drop=False`` raises ``ValueError`` instead of silently skipping a blocked
    key, for callers that must reject (not ignore) malicious payloads.
    """
    for k, v in source.items():
        if is_blocked_key(k):
            if not drop:
                raise ValueError(f"blocked prototype-polluting key: {k!r}")
            continue
        target[k] = strip_blocked_keys(v)
    return target


def fastapi_safe_dict(
    raw: Any, *, drop: bool = True
) -> Dict[str, Any]:
    """Coerce an untrusted request body into a Pydantic/FastAPI-safe dict.

    Strips ``__proto__``/``prototype``/``constructor`` at every depth before the
    payload is handed to a model validator or ORM ``**kwargs`` expansion.
    """
    return safe_update_dict({}, strip_blocked_keys(raw), drop=drop) if isinstance(raw, dict) else {}


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
    "strip_blocked_keys",
    "safe_load_json",
    "safe_update_dict",
    "fastapi_safe_dict",
    "report",
]

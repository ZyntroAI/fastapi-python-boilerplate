"""Tests for deliverables/cwe1321-protection-suite/python/safe_parser.py (CWE-1321)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from safe_parser import (  # noqa: E402
    fastapi_safe_dict,
    is_blocked_key,
    report,
    safe_load_json,
    safe_update_dict,
    strip_blocked_keys,
)


def test_blocked_key_detection():
    assert is_blocked_key("__proto__")
    assert is_blocked_key("prototype")
    assert is_blocked_key("constructor")
    assert not is_blocked_key("role")
    assert not is_blocked_key(123)


def test_strip_blocked_keys_drops_top_level():
    out = strip_blocked_keys({"__proto__": {"role": "admin"}, "name": "ok"})
    assert "__proto__" not in out
    assert out == {"name": "ok"}


def test_strip_blocked_keys_recursive():
    payload = {
        "a": {"b": {"__proto__": {"polluted": True}, "keep": 1}},
        "list": [{"constructor": "x", "keep": 2}],
    }
    out = strip_blocked_keys(payload)
    assert "__proto__" not in str(out)
    assert "constructor" not in str(out)
    assert out["a"]["b"]["keep"] == 1
    assert out["list"][0]["keep"] == 2


def test_safe_load_json_rejects_pollution():
    raw = '{"__proto__": {"role": "admin"}, "normal": true}'
    data = safe_load_json(raw)
    assert "__proto__" not in data
    assert data["normal"] is True
    # Verify the polluting key never reached the global object/class.
    assert not hasattr(dict, "role")


def test_safe_update_dict_drop_mode():
    target = {"existing": 1}
    out = safe_update_dict(target, {"__proto__": {"role": "admin"}, "new": 2})
    assert out == {"existing": 1, "new": 2}
    assert not hasattr(dict, "role")


def test_safe_update_dict_raise_mode():
    try:
        safe_update_dict({}, {"__proto__": {"role": "admin"}}, drop=False)
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_fastapi_safe_dict_coercion():
    body = {"user": {"__proto__": {"is_admin": True}, "name": "nattapong"}}
    safe = fastapi_safe_dict(body)
    assert "__proto__" not in safe["user"]
    assert safe["user"]["name"] == "nattapong"
    assert not hasattr(dict, "is_admin")


def test_report_shape():
    r = report(status="rejected", keys=["__proto__"], remediation="strip key")
    assert r == {
        "status": "rejected",
        "keys": ["__proto__"],
        "remediation": "strip key",
    }


def test_round_trip_json():
    payload = {"role": "user", "nested": {"__proto__": {"x": 1}, "y": 2}}
    data = safe_load_json(json.dumps(payload))
    assert data == {"role": "user", "nested": {"y": 2}}

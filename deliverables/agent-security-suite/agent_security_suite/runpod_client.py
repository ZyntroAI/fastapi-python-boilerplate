"""RunPod client — lazy `runpod` import, action schema validation, audit hook.

Distilled to the suite's lazy-dependency pattern (like recovery/mcp): importing
this module never requires the `runpod` package; it is only loaded when a
connection is actually opened via `connect_runpod()`.

Raises RuntimeError when `runpod` is not installed rather than failing at
import time.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

# Allowed top-level actions and the args they accept. Unknown actions are
# rejected before any network call.
ACTION_SCHEMA = {
    "get_user": {},
    "list_pods": {},
    "get_pod": {"pod_id": str},
    "stop_pod": {"pod_id": str},
    "resume_pod": {"pod_id": str},
}


def _get_runpod():
    """Return the runpod module or raise RuntimeError if unavailable."""
    try:
        import runpod  # lazy — only needed for a real connection
        return runpod
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "runpod is not installed. Install it to enable RunPod operations."
        ) from e


def _validate_action(action: str, params: Dict[str, Any]) -> Optional[str]:
    """Return an error string if the action/params are invalid, else None."""
    if action not in ACTION_SCHEMA:
        return f"unknown action: {action!r}"
    schema = ACTION_SCHEMA[action]
    for key, typ in schema.items():
        if key not in params or not isinstance(params.get(key), typ):
            return f"missing/invalid param: {key}"
    return None


class RunPodClient:
    def __init__(self, api_key: str, session_id: str, audit=None) -> None:
        self._api_key = api_key
        self._session_id = session_id
        self._audit = audit  # optional callable log_event-like hook
        self._rp = None

    def _audit_log(self, action: str, status: str, payload: Dict[str, Any], error: str = None) -> None:
        if self._audit is not None:
            try:
                self._audit(self._session_id, "runpod", action, "RUNPOD", status,
                            payload, error=error)
            except Exception:  # audit must never break the request
                pass

    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action against RunPod.

        Args:
            command: ``{"action": str, "params": {...}}`` (params optional).

        Returns:
            dict with ``status`` in {"invalid", "success", "error"}.
        """
        action = command.get("action")
        params = command.get("params", {})
        err = _validate_action(action, params)
        if err:
            self._audit_log(action, "INVALID", command, error=err)
            return {"status": "invalid", "error": err}

        if self._rp is None:
            rp = _get_runpod()  # may raise RuntimeError
            rp.api_key = self._api_key  # type: ignore
            self._rp = rp

        try:
            result = self._dispatch(action, params)
        except Exception as e:  # noqa: BLE001 - surface as error status
            self._audit_log(action, "ERROR", command, error=str(e))
            return {"status": "error", "error": str(e)}

        self._audit_log(action, "SUCCESS", command)
        return {"status": "success", "result": result}

    def _dispatch(self, action: str, params: Dict[str, Any]):
        # Thin mapping to runpod's public helpers. Real callers/params may
        # extend this; runpod is mocked in tests.
        rp = self._rp
        if action == "get_user":
            return rp.get_user()
        if action == "list_pods":
            return rp.get_pods()
        if action == "get_pod":
            return rp.get_pod(params["pod_id"])
        if action == "stop_pod":
            return rp.stop_pod(params["pod_id"])
        if action == "resume_pod":
            return rp.resume_pod(params["pod_id"])
        return {"note": f"no-op for {action}"}


def connect_runpod(session_id: str, api_key: Optional[str] = None, audit=None) -> RunPodClient:
    """Create a RunPod client. Reads ``RUNPOD_API_KEY`` from env if not given."""
    key = api_key or os.getenv("RUNPOD_API_KEY", "")
    if not key:
        raise RuntimeError("RUNPOD_API_KEY is not set")
    return RunPodClient(api_key=key, session_id=session_id, audit=audit)

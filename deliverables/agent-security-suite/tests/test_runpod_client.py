"""RunPod client tests — schema validation, lazy import, audit, dispatch (runpod mocked)."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_tmp = tempfile.mkdtemp()
os.environ["AUDIT_DB_PATH"] = os.path.join(_tmp, "audit_test.db")

import pytest
from unittest import mock

from agent_security_suite import runpod_client as rc
from agent_security_suite.runpod_client import RunPodClient, connect_runpod


def test_unknown_action_invalid():
    client = RunPodClient(api_key="k", session_id="s")
    res = client.execute({"action": "invalid"})
    assert res["status"] == "invalid"
    assert "unknown action" in res["error"]


def test_missing_param_invalid():
    client = RunPodClient(api_key="k", session_id="s")
    res = client.execute({"action": "get_pod"})  # pod_id missing
    assert res["status"] == "invalid"


def test_connect_runpod_requires_key():
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError):
            connect_runpod("s")


def test_lazy_import_raises_without_runpod():
    # Importing the module must not require runpod (already imported above OK).
    # _get_runpod() raises RuntimeError when runpod is absent.
    with mock.patch.dict("sys.modules", {"runpod": None}):
        with pytest.raises(RuntimeError):
            rc._get_runpod()


def test_execute_success_with_mocked_runpod():
    fake_rp = mock.MagicMock()
    fake_rp.get_user.return_value = {"id": "user1"}
    client = RunPodClient(api_key="k", session_id="s")
    with mock.patch.object(rc, "_get_runpod", return_value=fake_rp):
        res = client.execute({"action": "get_user"})
    assert res["status"] == "success"
    assert res["result"] == {"id": "user1"}
    fake_rp.get_user.assert_called_once()


def test_execute_pod_action():
    fake_rp = mock.MagicMock()
    fake_rp.get_pod.return_value = {"id": "pod1"}
    client = RunPodClient(api_key="k", session_id="s")
    with mock.patch.object(rc, "_get_runpod", return_value=fake_rp):
        res = client.execute({"action": "get_pod", "params": {"pod_id": "pod1"}})
    assert res["status"] == "success"
    fake_rp.get_pod.assert_called_once_with("pod1")


def test_audit_hook_called():
    calls = []
    def audit(sid, agent, action, resource, status, payload, error=None):
        calls.append((action, status))
    fake_rp = mock.MagicMock()
    fake_rp.get_user.return_value = {"id": "u"}
    client = RunPodClient(api_key="k", session_id="s", audit=audit)
    with mock.patch.object(rc, "_get_runpod", return_value=fake_rp):
        client.execute({"action": "get_user"})
    client.execute({"action": "bad"})
    assert ("get_user", "SUCCESS") in calls
    assert ("bad", "INVALID") in calls

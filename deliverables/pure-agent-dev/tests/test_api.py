"""API surface: routes are thin and the app boots without credentials."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from pure_agent.main import app


@pytest.fixture
def client(monkeypatch) -> TestClient:
    monkeypatch.setenv("COMPUTE_PROVIDER", "mock")
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_instances(client):
    r = client.get("/v1/compute/instances")
    assert r.status_code == 200
    assert len(r.json()) >= 1


@pytest.mark.parametrize(
    "action,verb",
    [("start", "start_instance"), ("stop", "stop_instance"), ("reboot", "reboot_instance")],
)
def test_instance_actions_over_http(client, action, verb):
    r = client.post(f"/v1/compute/instances/i-mock-001/{action}")
    assert r.status_code == 200
    body = r.json()
    assert body["instance_id"] == "i-mock-001"
    if verb != "list_instances":
        assert body["status"]


def test_run_structured_task(client):
    r = client.post(
        "/v1/tasks",
        json={"task_id": "t-1", "action": "start_instance", "instance_id": "i-mock-001"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "starting"


def test_run_task_rejects_unknown_action(client):
    r = client.post("/v1/tasks", json={"task_id": "t", "action": "drop_database"})
    assert r.status_code == 422


def test_run_task_rejects_missing_instance_id(client):
    r = client.post("/v1/tasks", json={"task_id": "t", "action": "start_instance"})
    assert r.status_code == 422


def test_openapi_documents_every_route(client):
    paths = client.get("/openapi.json").json()["paths"]
    for expected in (
        "/health",
        "/v1/tasks",
        "/v1/compute/instances",
        "/v1/compute/instances/{instance_id}/start",
        "/v1/compute/instances/{instance_id}/stop",
        "/v1/compute/instances/{instance_id}/reboot",
    ):
        assert expected in paths

"""Provider contract: every adapter must behave identically."""

from __future__ import annotations

import inspect

import pytest

from pure_agent.providers.base import ComputeProvider
from pure_agent.providers.mock import MockComputeProvider
from pure_agent.schemas.compute import InstanceResponse


class FailingProvider(ComputeProvider):
    """A second implementation, to prove the interface is genuinely abstract."""

    async def list_instances(self):
        raise RuntimeError("list not supported")

    async def start_instance(self, instance_id):
        return InstanceResponse(instance_id=instance_id, status="starting")

    async def stop_instance(self, instance_id):
        return InstanceResponse(instance_id=instance_id, status="stopping")

    async def reboot_instance(self, instance_id):
        return InstanceResponse(instance_id=instance_id, status="rebooting")


def test_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        ComputeProvider()  # type: ignore[abstract]


@pytest.mark.provider
@pytest.mark.parametrize("provider_cls", [MockComputeProvider, FailingProvider])
async def test_every_provider_implements_the_contract(provider_cls):
    provider = provider_cls()
    for method in ("list_instances", "start_instance", "stop_instance", "reboot_instance"):
        assert callable(getattr(provider, method))
        assert inspect.iscoroutinefunction(getattr(provider, method))


@pytest.mark.provider
async def test_mock_returns_normalised_responses():
    provider = MockComputeProvider(instances=["i-a"])
    assert all(isinstance(i, InstanceResponse) for i in await provider.list_instances())
    for method in ("start_instance", "stop_instance", "reboot_instance"):
        resp = await getattr(provider, method)("i-a")
        assert isinstance(resp, InstanceResponse)
        assert resp.instance_id == "i-a"


@pytest.mark.provider
async def test_mock_status_transitions_are_observable():
    provider = MockComputeProvider(instances=["i-a"])
    await provider.stop_instance("i-a")
    inst = (await provider.list_instances())[0]
    assert inst.status == "stopping"


@pytest.mark.provider
def test_byteplus_adapter_satisfies_the_interface_without_sdk_or_credentials():
    """The adapter must be constructible and structurally correct with no SDK present."""
    from pure_agent.providers.byteplus.client import BytePlusClient
    from pure_agent.providers.byteplus.ecs import BytePlusECSProvider

    client = BytePlusClient(access_key="k", secret_key="s", region="ap-southeast-1")
    provider = BytePlusECSProvider(client)
    assert isinstance(provider, ComputeProvider)
    assert client.get_region() == "ap-southeast-1"
    assert not isinstance(provider, MockComputeProvider)


@pytest.mark.provider
def test_byteplus_client_reports_missing_credentials(monkeypatch):
    from pure_agent.providers.byteplus.client import BytePlusClient, MissingCredentialError

    monkeypatch.delenv("BYTEPLUS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("BYTEPLUS_SECRET_KEY", raising=False)
    with pytest.raises(MissingCredentialError) as exc:
        BytePlusClient.from_env()
    assert "BYTEPLUS_ACCESS_KEY" in str(exc.value)


@pytest.mark.provider
def test_byteplus_client_reads_region_from_env(monkeypatch):
    from pure_agent.providers.byteplus.client import BytePlusClient

    monkeypatch.setenv("BYTEPLUS_ACCESS_KEY", "k")
    monkeypatch.setenv("BYTEPLUS_SECRET_KEY", "s")
    monkeypatch.setenv("BYTEPLUS_REGION", "eu-central-1")
    assert BytePlusClient.from_env().get_region() == "eu-central-1"

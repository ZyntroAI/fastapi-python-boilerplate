"""Integration tests that hit the real Paddle SANDBOX API.

Opt-in: these run only with ``pytest --run-integration`` AND sandbox
credentials in ``PADDLE_SANDBOX_API_KEY``. The safety guard in ``conftest.py``
forces the sandbox host and rejects live keys, so this cannot touch a live
Paddle account. Customers created here are deleted on teardown.
"""
import pytest
import requests

from app.billing import ProviderNotFoundError
from app.paddle import PaddleBillingProvider

pytestmark = pytest.mark.integration


@pytest.fixture
def provider(paddle_sandbox):
    key, base = paddle_sandbox
    p = PaddleBillingProvider(api_key=key, base_url=base)
    created: list[str] = []
    yield p, created
    headers = {"Authorization": f"Bearer {key}"}
    for cid in created:
        try:
            requests.delete(f"{base}/customers/{cid}", headers=headers, timeout=15)
        except requests.RequestException:
            pass


def test_health_reports_test_mode(provider):
    p, _ = provider
    health = p.health()
    assert health["provider"] == "paddle"
    assert health["mode"] == "test"


def test_create_and_get_customer(provider):
    p, created = provider
    c = p.create_customer("integration-cus@example.com", name="Integration Test")
    created.append(c.id)
    assert c.id.startswith("ctm_")
    assert c.email == "integration-cus@example.com"

    fetched = p.get_customer(c.id)
    assert fetched.id == c.id
    assert fetched.email == c.email


def test_create_invoice(provider):
    p, created = provider
    c = p.create_customer("integration-inv@example.com")
    created.append(c.id)
    inv = p.create_invoice(
        c.id, amount=2500, currency="usd", description="Integration invoice"
    )
    assert inv.customer_id == c.id
    assert inv.amount == 2500
    assert inv.id


def test_charge(provider):
    p, created = provider
    c = p.create_customer("integration-pi@example.com")
    created.append(c.id)
    pi = p.charge(c.id, amount=1200, currency="usd")
    assert pi.customer_id == c.id
    assert pi.amount == 1200
    assert pi.id


def test_missing_customer_raises_not_found(provider):
    p, _ = provider
    with pytest.raises(ProviderNotFoundError):
        p.get_customer("ctm_does_not_exist_12345")

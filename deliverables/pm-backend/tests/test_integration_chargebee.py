"""Integration tests that hit the real Chargebee TEST site.

Opt-in: these run only with ``pytest --run-integration`` AND test-site
credentials in ``CHARGEBEE_TEST_API_KEY`` / ``CHARGEBEE_TEST_SITE``. The safety
guard in ``conftest.py`` requires a ``*-test`` site, so this cannot touch a
production Chargebee account. Customers created here are deleted on teardown.
"""
import base64

import pytest
import requests

from app.billing import ProviderNotFoundError
from app.chargebee import ChargebeeBillingProvider

pytestmark = pytest.mark.integration


def _basic_auth(key: str) -> str:
    token = base64.b64encode(f"{key}:".encode()).decode()
    return f"Basic {token}"


@pytest.fixture
def provider(chargebee_test_site):
    key, base = chargebee_test_site
    p = ChargebeeBillingProvider(api_key=key, base_url=base)
    created: list[str] = []
    yield p, created
    headers = {"Authorization": _basic_auth(key)}
    for cid in created:
        try:
            # Chargebee deletes via POST /customers/<id>/delete
            requests.post(
                f"{base}/customers/{cid}/delete", headers=headers, timeout=15
            )
        except requests.RequestException:
            pass


def test_health_reports_test_mode(provider):
    p, _ = provider
    health = p.health()
    assert health["provider"] == "chargebee"
    assert health["mode"] == "test"


def test_create_and_get_customer(provider):
    p, created = provider
    c = p.create_customer("integration-cus@example.com", name="Integration Test")
    created.append(c.id)
    assert c.id
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
        p.get_customer("__does_not_exist__")

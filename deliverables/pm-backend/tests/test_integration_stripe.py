"""Integration tests that hit the real Stripe TEST API.

Opt-in: these run only with ``pytest --run-integration`` AND a test-mode key in
``STRIPE_TEST_API_KEY``. The safety guard in ``conftest.py`` refuses live keys,
so this can never touch a production account. Customers created here are
deleted on teardown.
"""
import pytest

from app.billing import ProviderNotFoundError, StripeBillingProvider

pytestmark = pytest.mark.integration


@pytest.fixture
def provider(stripe_test_key):
    p = StripeBillingProvider(api_key=stripe_test_key)
    created: list[str] = []
    yield p, created
    # Best-effort teardown so repeated runs don't accumulate test customers.
    import stripe

    for cid in created:
        try:
            stripe.Customer.delete(cid)
        except Exception:
            pass


def test_health_reports_test_mode(provider):
    p, _ = provider
    health = p.health()
    assert health["provider"] == "stripe"
    assert health["mode"] == "test"


def test_create_and_get_customer(provider):
    p, created = provider
    c = p.create_customer("integration+cus@example.com", name="Integration Test")
    created.append(c.id)
    assert c.id.startswith("cus_")
    assert c.email == "integration+cus@example.com"
    assert c.name == "Integration Test"

    fetched = p.get_customer(c.id)
    assert fetched.id == c.id
    assert fetched.email == c.email


def test_create_invoice(provider):
    p, created = provider
    c = p.create_customer("integration+inv@example.com")
    created.append(c.id)
    inv = p.create_invoice(
        c.id, amount=2500, currency="usd", description="Integration invoice"
    )
    assert inv.customer_id == c.id
    assert inv.amount == 2500
    assert inv.status in {"open", "draft", "paid"}


def test_charge(provider):
    p, created = provider
    c = p.create_customer("integration+pi@example.com")
    created.append(c.id)
    pi = p.charge(c.id, amount=1200, currency="usd")
    assert pi.customer_id == c.id
    assert pi.amount == 1200
    assert pi.status


def test_missing_customer_raises_not_found(provider):
    p, _ = provider
    with pytest.raises(ProviderNotFoundError):
        p.get_customer("cus_does_not_exist_12345")

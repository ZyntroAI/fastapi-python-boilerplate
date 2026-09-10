"""Tests for the real Stripe billing adapter, verified with a mocked SDK.

We cannot call Stripe's live API without a test-mode key, so we assert the
adapter drives the Stripe SDK correctly by replacing the SDK's resource
classes with fakes that mimic real Stripe objects (dict-like, keyed access).
This validates the adapter's calls, argument translation, and error mapping
against the semantics Stripe actually returns.
"""
from types import ModuleType
import sys

import pytest

from app.billing import (
    ProviderAuthError,
    ProviderNotFoundError,
    StripeBillingProvider,
    build_provider,
)


# --- Fake Stripe SDK --------------------------------------------------------

class FakeCustomer(dict):
    @classmethod
    def create(cls, **kw):
        return cls(id="cus_test123", email=kw.get("email", ""), name=kw.get("name", ""))

    @classmethod
    def retrieve(cls, customer_id):
        if customer_id == "missing":
            raise _make_stripe_error("InvalidRequestError", "No such customer")
        return cls(id=customer_id, email="e@x.com", name="X")


class FakeInvoiceItem(dict):
    @classmethod
    def create(cls, **kw):
        return cls(id="ii_test", **kw)


class FakeInvoice(dict):
    @classmethod
    def create(cls, **kw):
        return cls(id="in_test_draft", customer=kw.get("customer", ""), status="draft")

    @classmethod
    def finalize_invoice(cls, invoice_id):
        return cls(id=invoice_id, status="open")


class FakePaymentIntent(dict):
    @classmethod
    def create(cls, **kw):
        return cls(
            id="pi_test123",
            amount=kw.get("amount", 0),
            currency=kw.get("currency", "usd"),
            customer=kw.get("customer", ""),
            status="requires_payment_method",
        )


class _FakeErrors:
    class Error(Exception):
        pass

    class AuthenticationError(Error):
        pass

    class InvalidRequestError(Error):
        pass

    class CardError(Error):
        pass


class FakeStripe(ModuleType):
    api_key = "sk_test_dummy"
    api_base = "https://api.stripe.com"
    Customer = FakeCustomer
    Invoice = FakeInvoice
    InvoiceItem = FakeInvoiceItem
    PaymentIntent = FakePaymentIntent
    error = _FakeErrors


def _make_stripe_error(kind, msg):
    exc = getattr(_FakeErrors, kind)(msg)
    # Stripe SDK error objects expose an attribute-style payload.
    exc.error = type("E", (), {"message": msg})()
    return exc


@pytest.fixture
def fake_stripe_module():
    """Inject a fake Stripe module into sys.modules so the adapter's lazy
    ``import stripe`` picks it up, and restore the real module after."""
    real = sys.modules.get("stripe")
    fake = FakeStripe("stripe")
    sys.modules["stripe"] = fake
    try:
        yield fake
    finally:
        if real is not None:
            sys.modules["stripe"] = real
        else:
            sys.modules.pop("stripe", None)


def _provider(fake_stripe_module) -> StripeBillingProvider:
    return StripeBillingProvider(api_key="sk_test_dummy")


# --- Construction -----------------------------------------------------------

def test_requires_api_key():
    with pytest.raises(ProviderAuthError):
        StripeBillingProvider(api_key="")


def test_missing_key_at_factory_raises():
    with pytest.raises(ProviderAuthError):
        build_provider(provider="stripe", api_key="", base_url="")


def test_detects_test_mode(fake_stripe_module):
    assert _provider(fake_stripe_module)._mode == "test"


def test_detects_live_mode(fake_stripe_module):
    p = StripeBillingProvider(api_key="sk_live_abc")
    assert p._mode == "live"


# --- Customer lifecycle -----------------------------------------------------

def test_create_customer(fake_stripe_module):
    p = _provider(fake_stripe_module)
    c = p.create_customer("a@b.com", name="Alice")
    assert c.id == "cus_test123"
    assert c.email == "a@b.com"
    assert c.name == "Alice"


def test_get_customer_ok(fake_stripe_module):
    c = _provider(fake_stripe_module).get_customer("cus_known")
    assert c.id == "cus_known"


def test_get_missing_customer_raises_not_found(fake_stripe_module):
    with pytest.raises(ProviderNotFoundError):
        _provider(fake_stripe_module).get_customer("missing")


# --- Invoice lifecycle ------------------------------------------------------

def test_create_invoice_flow(fake_stripe_module):
    """create_invoice must: create draft -> add line item -> finalize."""
    # Replace the fake resource methods with mocks so we can assert the
    # adapter really drives all three Stripe calls with correct arguments.
    sm = fake_stripe_module
    from unittest.mock import Mock

    sm.Invoice.create = Mock(return_value=sm.Invoice(id="in_draft", status="draft"))
    sm.InvoiceItem.create = Mock(return_value=sm.InvoiceItem(id="ii_1"))
    sm.Invoice.finalize_invoice = Mock(
        return_value=sm.Invoice(id="in_draft", status="open")
    )

    p = _provider(fake_stripe_module)
    inv = p.create_invoice("cus_test123", amount=2500, currency="usd",
                           description="Setup")

    sm.Invoice.create.assert_called_once_with(customer="cus_test123")
    sm.InvoiceItem.create.assert_called_once_with(
        customer="cus_test123", amount=2500, currency="usd",
        description="Setup", invoice="in_draft",
    )
    sm.Invoice.finalize_invoice.assert_called_once_with("in_draft")
    assert inv.id == "in_draft"
    assert inv.status == "open"
    assert inv.amount == 2500


# --- Charges ----------------------------------------------------------------

def test_charge_creates_payment_intent(fake_stripe_module):
    pi = _provider(fake_stripe_module).charge("cus_test123", 1200, "usd")
    assert pi.id == "pi_test123"
    assert pi.amount == 1200
    assert pi.status == "requires_payment_method"


def test_missing_customer_charge_maps_to_provider_error(fake_stripe_module):
    # The adapter should surface Stripe errors; our fake customer validation
    # only triggers on get_customer, so simulate by patching create.
    fake_stripe_module.PaymentIntent = type(
        "BadPI", (), {"create": staticmethod(lambda **kw: (_ for _ in ()).throw(
            _make_stripe_error("InvalidRequestError", "No such customer: cus_x")
        ))}
    )
    with pytest.raises(ProviderNotFoundError):
        _provider(fake_stripe_module).charge("cus_x", 100, "usd")


# --- Error translation ------------------------------------------------------

def test_auth_error_maps_to_provider_auth(fake_stripe_module):
    fake_stripe_module.Customer = type(
        "BadCust", (), {"create": staticmethod(lambda **kw: (_ for _ in ()).throw(
            _make_stripe_error("AuthenticationError", "Invalid API key")
        ))}
    )
    with pytest.raises(ProviderAuthError):
        _provider(fake_stripe_module).create_customer("a@b.com")


def test_health_reports_mode(fake_stripe_module):
    h = _provider(fake_stripe_module).health()
    assert h["provider"] == "stripe"
    assert h["mode"] == "test"

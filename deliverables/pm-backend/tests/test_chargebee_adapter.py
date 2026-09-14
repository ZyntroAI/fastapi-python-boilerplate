"""Tests for the Chargebee billing adapter, verified against a mocked HTTP
layer (we do not call Chargebee's live API without a key). A fake ``requests``
records the outbound calls and returns canned Chargebee responses so we assert
the adapter builds the right requests and maps errors correctly.
"""
import sys
from types import ModuleType

import pytest

from app.billing import (
    ProviderAuthError,
    ProviderNotFoundError,
    build_provider,
)
from app.chargebee import ChargebeeBillingProvider


# --- Fake requests layer ----------------------------------------------------

class _FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.ok = 200 <= status_code < 300
        self.text = str(json_data)

    def json(self):
        return self._json


class FakeRequests(ModuleType):
    """Module stand-in: records calls, returns configurable responses. The
    adapter's own status-code handling raises the provider errors, so this
    fake only returns queued responses (never raises)."""

    responses: list[_FakeResponse] = []
    calls: list[tuple] = []
    # Present so the adapter's ``except requests.RequestException`` clause
    # resolves without error (it is only evaluated on a transport failure).
    RequestException = Exception

    @classmethod
    def reset(cls, *responses):
        cls.responses = list(responses) or [_FakeResponse()]
        cls.calls = []

    @classmethod
    def request(cls, method, url, **kwargs):
        cls.calls.append((method, url, kwargs))
        return cls.responses.pop(0) if cls.responses else _FakeResponse()


@pytest.fixture
def fake_requests():
    real = sys.modules.get("requests")
    fake = FakeRequests("requests")
    sys.modules["requests"] = fake
    FakeRequests.reset()
    try:
        yield fake
    finally:
        if real is not None:
            sys.modules["requests"] = real
        else:
            sys.modules.pop("requests", None)


def _provider():
    return ChargebeeBillingProvider(
        api_key="cb_test_key",
        base_url="https://acme-test.chargebee.com/api/v2",
    )


# --- Construction -----------------------------------------------------------

def test_requires_api_key():
    with pytest.raises(ProviderAuthError):
        ChargebeeBillingProvider(api_key="", base_url="https://x/api/v2")


def test_requires_base_url():
    with pytest.raises(ProviderAuthError):
        ChargebeeBillingProvider(api_key="cb_key", base_url="")


def test_detects_mode_from_site():
    assert _provider()._mode == "test"
    live = ChargebeeBillingProvider(
        api_key="cb_key", base_url="https://acme.chargebee.com/api/v2"
    )
    assert live._mode == "live"


def test_factory_registers_chargebee(fake_requests):
    p = build_provider(
        provider="chargebee", api_key="cb_key",
        base_url="https://x-test.chargebee.com/api/v2",
    )
    assert p.name == "chargebee"


# --- Customer ---------------------------------------------------------------

def test_create_customer(fake_requests):
    FakeRequests.reset(_FakeResponse(200, {"customer": {
        "id": "cb_cus_1", "email": "a@b.com",
        "first_name": "Alice", "last_name": "Smith",
    }}))
    p = _provider()
    c = p.create_customer("a@b.com", name="Alice Smith")
    assert c.id == "cb_cus_1"
    assert c.name == "Alice Smith"
    # Assert it POSTed to /customers with the right JSON body.
    method, url, kwargs = FakeRequests.calls[0]
    assert method == "POST" and url.endswith("/customers")
    assert kwargs["json"]["customer"]["email"] == "a@b.com"


def test_get_customer_ok(fake_requests):
    FakeRequests.reset(_FakeResponse(200, {"customer": {
        "id": "cb_cus_9", "email": "e@x.com", "first_name": "X",
    }}))
    c = _provider().get_customer("cb_cus_9")
    assert c.id == "cb_cus_9"
    assert c.email == "e@x.com"


def test_get_missing_customer_raises_not_found(fake_requests):
    FakeRequests.reset(_FakeResponse(404, {"error": "not found"}))
    # 404 -> ProviderNotFoundError (mapped to HTTP 404 by the router)
    with pytest.raises(ProviderNotFoundError):
        _provider().get_customer("nope")


def test_bad_key_raises_auth_error(fake_requests):
    FakeRequests.reset(_FakeResponse(401))
    with pytest.raises(ProviderAuthError):
        _provider().get_customer("cb_cus_1")


# --- Invoice / charge -------------------------------------------------------

def test_create_invoice(fake_requests):
    FakeRequests.reset(_FakeResponse(200, {"invoice": {
        "id": "cb_inv_1", "status": "posted",
    }}))
    inv = _provider().create_invoice("cb_cus_1", 2500, "usd", "Setup")
    method, url, kwargs = FakeRequests.calls[0]
    assert method == "POST" and url.endswith("/invoices")
    # Amount is sent in major units (25.00) with currency uppercased.
    assert kwargs["json"]["invoice"]["addons"][0]["amount"] == 25.0
    assert kwargs["json"]["invoice"]["currency_code"] == "USD"
    assert inv.id == "cb_inv_1"
    assert inv.amount == 2500


def test_charge_creates_payment_intent(fake_requests):
    FakeRequests.reset(_FakeResponse(200, {"payment_intent": {
        "id": "cb_pi_1", "status": "inited",
    }}))
    pi = _provider().charge("cb_cus_1", 1200, "usd")
    method, url, kwargs = FakeRequests.calls[0]
    assert method == "POST" and url.endswith("/payment_intents")
    assert kwargs["json"]["payment_intent"]["amount"] == 12.0
    assert pi.id == "cb_pi_1"
    assert pi.amount == 1200

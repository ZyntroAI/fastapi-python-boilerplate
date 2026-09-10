"""Tests for the Paddle billing adapter, verified against a mocked HTTP layer
(no live Paddle key). A fake ``requests`` records outbound calls and returns
canned Paddle Billing responses (wrapped in ``{"data": ...}``) so we assert the
adapter builds correct requests and maps errors to the neutral hierarchy.
"""
import sys
from types import ModuleType

import pytest

from app.billing import ProviderAuthError, ProviderNotFoundError, build_provider
from app.paddle import PaddleBillingProvider


class _FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.ok = 200 <= status_code < 300
        self.text = str(json_data)

    def json(self):
        return self._json


class FakeRequests(ModuleType):
    """Returns queued responses; the adapter's own status handling raises."""

    responses: list[_FakeResponse] = []
    calls: list[tuple] = []
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
    return PaddleBillingProvider(api_key="pdl_test_key")


# --- Construction -----------------------------------------------------------

def test_requires_api_key():
    with pytest.raises(ProviderAuthError):
        PaddleBillingProvider(api_key="")


def test_defaults_to_live_mode():
    assert _provider()._mode == "live"


def test_sandbox_url_is_test_mode():
    p = PaddleBillingProvider(
        api_key="pdl_key", base_url="https://sandbox-api.paddle.com"
    )
    assert p._mode == "test"


def test_factory_registers_paddle(fake_requests):
    p = build_provider(provider="paddle", api_key="pdl_key", base_url="")
    assert p.name == "paddle"


# --- Customer ---------------------------------------------------------------

def test_create_customer(fake_requests):
    FakeRequests.reset(_FakeResponse(200, {"data": {
        "id": "ctm_1", "email": "a@b.com", "name": "Alice",
    }}))
    c = _provider().create_customer("a@b.com", name="Alice")
    assert c.id == "ctm_1"
    assert c.name == "Alice"
    method, url, kwargs = FakeRequests.calls[0]
    assert method == "POST" and url.endswith("/customers")
    assert kwargs["json"] == {"email": "a@b.com", "name": "Alice"}
    # Bearer auth header is set.
    assert kwargs["headers"]["Authorization"] == "Bearer pdl_test_key"


def test_get_customer_ok(fake_requests):
    FakeRequests.reset(_FakeResponse(200, {"data": {
        "id": "ctm_9", "email": "e@x.com",
    }}))
    c = _provider().get_customer("ctm_9")
    assert c.id == "ctm_9"
    assert c.email == "e@x.com"


def test_get_missing_customer_raises_not_found(fake_requests):
    FakeRequests.reset(_FakeResponse(404, {"error": "not found"}))
    with pytest.raises(ProviderNotFoundError):
        _provider().get_customer("nope")


def test_bad_key_raises_auth_error(fake_requests):
    FakeRequests.reset(_FakeResponse(401))
    with pytest.raises(ProviderAuthError):
        _provider().get_customer("ctm_1")


# --- Transaction / invoice / charge -----------------------------------------

def test_create_invoice_uses_manual_collection(fake_requests):
    FakeRequests.reset(_FakeResponse(200, {"data": {
        "id": "txn_1", "status": "draft",
    }}))
    inv = _provider().create_invoice("ctm_1", 2500, "usd", "Setup")
    method, url, kwargs = FakeRequests.calls[0]
    assert method == "POST" and url.endswith("/transactions")
    body = kwargs["json"]
    assert body["collection_mode"] == "manual"
    assert body["customer_id"] == "ctm_1"
    # Amount is a minor-unit STRING with uppercased currency.
    price = body["items"][0]["price"]
    assert price["unit_price"]["amount"] == "2500"
    assert price["unit_price"]["currency_code"] == "USD"
    assert price["description"] == "Setup"
    assert inv.id == "txn_1"
    assert inv.amount == 2500
    assert inv.status == "draft"


def test_charge_uses_automatic_collection(fake_requests):
    FakeRequests.reset(_FakeResponse(200, {"data": {
        "id": "txn_2", "status": "ready",
    }}))
    pi = _provider().charge("ctm_1", 1200, "usd")
    body = FakeRequests.calls[0][2]["json"]
    assert body["collection_mode"] == "automatic"
    assert body["items"][0]["price"]["unit_price"]["amount"] == "1200"
    assert pi.id == "txn_2"
    assert pi.amount == 1200
    assert pi.status == "ready"


def test_upstream_error_is_provider_error(fake_requests):
    from app.billing import ProviderError

    FakeRequests.reset(_FakeResponse(500, {"error": "boom"}))
    with pytest.raises(ProviderError):
        _provider().get_customer("ctm_1")

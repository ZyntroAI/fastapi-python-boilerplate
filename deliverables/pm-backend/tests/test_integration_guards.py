"""Unit tests for the integration-test safety guards.

These are plain unit tests (no network, no opt-in needed): they prove the
guards refuse live credentials/sites and accept test ones, so a misconfigured
environment can never point an integration test at a production account.
"""
import pytest

from conftest import (
    LiveCredentialError,
    guard_chargebee_site,
    guard_paddle_sandbox,
    guard_stripe_key,
)


# --- Stripe ---------------------------------------------------------------

def test_stripe_accepts_test_secret_key():
    assert guard_stripe_key("sk_test_abc123") == "sk_test_abc123"


def test_stripe_accepts_test_restricted_key():
    assert guard_stripe_key("rk_test_abc123") == "rk_test_abc123"


def test_stripe_rejects_live_secret_key():
    with pytest.raises(LiveCredentialError, match="LIVE"):
        guard_stripe_key("sk_live_abc123")


def test_stripe_rejects_live_restricted_key():
    with pytest.raises(LiveCredentialError, match="LIVE"):
        guard_stripe_key("rk_live_abc123")


def test_stripe_rejects_unknown_key_shape():
    with pytest.raises(LiveCredentialError, match="test-mode"):
        guard_stripe_key("nonsense")


def test_stripe_rejects_empty_key():
    with pytest.raises(LiveCredentialError):
        guard_stripe_key("")


# --- Paddle ---------------------------------------------------------------

def test_paddle_accepts_sandbox():
    key, base = guard_paddle_sandbox("pdl_sdbx_abc", "https://sandbox-api.paddle.com")
    assert base == "https://sandbox-api.paddle.com"


def test_paddle_rejects_live_base_url():
    with pytest.raises(LiveCredentialError, match="sandbox-api"):
        guard_paddle_sandbox("pdl_abc", "https://api.paddle.com")


def test_paddle_rejects_live_key_marker():
    with pytest.raises(LiveCredentialError, match="LIVE"):
        guard_paddle_sandbox("pdl_live_abc", "https://sandbox-api.paddle.com")


# --- Chargebee ------------------------------------------------------------

def test_chargebee_accepts_test_site():
    key, base = guard_chargebee_site("cb_key", "acme-test")
    assert base == "https://acme-test.chargebee.com/api/v2"


def test_chargebee_rejects_production_site():
    with pytest.raises(LiveCredentialError, match="non-test"):
        guard_chargebee_site("cb_key", "acme")


def test_chargebee_rejects_empty_site():
    with pytest.raises(LiveCredentialError):
        guard_chargebee_site("cb_key", "")

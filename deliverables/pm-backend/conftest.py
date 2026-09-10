"""Shared pytest configuration.

Adds the project root to ``sys.path`` so ``from app import ...`` resolves, and
wires the opt-in harness for integration tests that hit real provider
sandboxes (Stripe / Paddle / Chargebee).

Integration tests are SKIPPED by default and only run with ``--run-integration``
AND the relevant credentials in the environment. Guards below refuse to run
against production keys/sites, so a misconfigured environment fails loudly
instead of touching a live account.
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# --------------------------------------------------------------------------
# Opt-in harness
# --------------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests that call real provider sandbox APIs",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: hits a real provider sandbox API "
        "(opt-in via --run-integration)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-integration"):
        return
    skip = pytest.mark.skip(
        reason="integration test — pass --run-integration (and set credentials) to run"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


# --------------------------------------------------------------------------
# Safety guards (pure functions so they can be unit-tested)
# --------------------------------------------------------------------------

class LiveCredentialError(ValueError):
    """Raised when an integration test is pointed at production credentials."""


def guard_stripe_key(key: str) -> str:
    """Allow only Stripe TEST-mode secret/restricted keys."""
    key = (key or "").strip()
    if key.startswith(("sk_live_", "rk_live_")):
        raise LiveCredentialError(
            "refusing to run integration tests with a LIVE Stripe key"
        )
    if not key.startswith(("sk_test_", "rk_test_")):
        raise LiveCredentialError(
            "Stripe integration tests require a test-mode key "
            "(sk_test_... or rk_test_...)"
        )
    return key


def guard_paddle_sandbox(key: str, base_url: str) -> tuple[str, str]:
    """Force the Paddle sandbox host and reject obviously-live keys."""
    key = (key or "").strip()
    base_url = (base_url or "").strip()
    if "live" in key.lower():
        raise LiveCredentialError(
            "refusing to run integration tests with a LIVE Paddle key"
        )
    if base_url != "https://sandbox-api.paddle.com":
        raise LiveCredentialError(
            "Paddle integration tests must target "
            "https://sandbox-api.paddle.com"
        )
    return key, base_url


def guard_chargebee_site(key: str, site: str) -> tuple[str, str]:
    """Require a Chargebee ``*-test`` site."""
    key = (key or "").strip()
    site = (site or "").strip()
    if not site.endswith("-test"):
        raise LiveCredentialError(
            "refusing to run integration tests against a non-test Chargebee "
            "site (expected '<name>-test')"
        )
    return key, f"https://{site}.chargebee.com/api/v2"


# --------------------------------------------------------------------------
# Credential fixtures
# --------------------------------------------------------------------------

def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        pytest.skip(f"{name} not set — skipping integration test")
    return value


@pytest.fixture
def stripe_test_key():
    key = _require_env("STRIPE_TEST_API_KEY")
    try:
        return guard_stripe_key(key)
    except LiveCredentialError as exc:
        pytest.fail(str(exc))


@pytest.fixture
def paddle_sandbox():
    key = _require_env("PADDLE_SANDBOX_API_KEY")
    base = os.getenv("PADDLE_SANDBOX_BASE_URL", "https://sandbox-api.paddle.com")
    try:
        return guard_paddle_sandbox(key, base)
    except LiveCredentialError as exc:
        pytest.fail(str(exc))


@pytest.fixture
def chargebee_test_site():
    key = _require_env("CHARGEBEE_TEST_API_KEY")
    site = _require_env("CHARGEBEE_TEST_SITE")
    try:
        return guard_chargebee_site(key, site)
    except LiveCredentialError as exc:
        pytest.fail(str(exc))

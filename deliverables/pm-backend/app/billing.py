"""Billing interoperability.

A provider-neutral billing interface so the backend can talk to any billing
provider (Stripe, Chargebee, a custom gateway, ...) without the rest of the
app knowing which one is behind it. Only the adapter for the *selected*
provider (``BILLING_PROVIDER``) is loaded; the default ``stub`` adapter
requires no network and no credentials, so the app runs out of the box.

Adapters signal failures through the provider-error hierarchy below so the
HTTP layer can map them to status codes without knowing provider internals:
    ProviderAuthError    -> 401/400 (bad key)
    ProviderNotFoundError-> 404 (resource missing at the provider)
    ProviderError        -> 502 (upstream failure)
"""
from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field


class ProviderError(Exception):
    """Base class for billing provider failures surfaced to the API layer."""


class ProviderNotFoundError(ProviderError):
    """A requested resource does not exist at the provider. -> HTTP 404."""


class ProviderAuthError(ProviderError):
    """The provider rejected the configured API key/credentials."""


class Customer(BaseModel):
    id: str
    email: str = ""
    name: str = ""
    currency: str = "usd"


class Invoice(BaseModel):
    id: str
    customer_id: str
    amount: int = Field(..., description="Amount in minor units")
    currency: str = "usd"
    status: str = "draft"
    description: str = ""


class PaymentIntent(BaseModel):
    id: str
    customer_id: str
    amount: int
    currency: str = "usd"
    status: str = "requires_confirmation"


class BillingProvider(Protocol):
    """The interface every billing adapter implements."""

    name: str

    def create_customer(self, email: str, name: str = "") -> Customer: ...
    def get_customer(self, customer_id: str) -> Customer: ...
    def create_invoice(
        self, customer_id: str, amount: int, currency: str = "usd",
        description: str = "",
    ) -> Invoice: ...
    def charge(
        self, customer_id: str, amount: int, currency: str = "usd",
    ) -> PaymentIntent: ...
    def health(self) -> dict: ...


class StubBillingProvider:
    """Offline adapter used by default. Useful for dev/tests and as the
    reference implementation for writing real provider adapters."""

    name = "stub"

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self.base_url = base_url
        self.api_key = api_key
        self._customers: dict[str, Customer] = {}
        self._invoices: dict[str, Invoice] = {}
        self._intents: dict[str, PaymentIntent] = {}
        self._seq = 0

    def _next_id(self, prefix: str) -> str:
        self._seq += 1
        return f"{prefix}_{self._seq:06d}"

    def create_customer(self, email: str, name: str = "") -> Customer:
        c = Customer(id=self._next_id("cus"), email=email, name=name)
        self._customers[c.id] = c
        return c

    def get_customer(self, customer_id: str) -> Customer:
        if customer_id not in self._customers:
            raise ProviderNotFoundError(f"customer not found: {customer_id}")
        return self._customers[customer_id]

    def create_invoice(
        self, customer_id: str, amount: int, currency: str = "usd",
        description: str = "",
    ) -> Invoice:
        if customer_id not in self._customers:
            raise ProviderNotFoundError(f"customer not found: {customer_id}")
        inv = Invoice(
            id=self._next_id("in_"),
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status="open",
            description=description,
        )
        self._invoices[inv.id] = inv
        return inv

    def charge(
        self, customer_id: str, amount: int, currency: str = "usd",
    ) -> PaymentIntent:
        if customer_id not in self._customers:
            raise ProviderNotFoundError(f"customer not found: {customer_id}")
        pi = PaymentIntent(
            id=self._next_id("pi_"),
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status="succeeded",
        )
        self._intents[pi.id] = pi
        return pi

    def health(self) -> dict:
        return {
            "provider": self.name,
            "status": "ok",
            "mode": "offline",
            "detail": "stub adapter (offline, no credentials required)",
        }


class StripeBillingProvider:
    """Real adapter backed by the stripe SDK.

    Only instantiated when BILLING_PROVIDER=stripe; the stripe package is
    imported lazily so the app has no hard dependency on it unless the
    provider is actually enabled.

    Raises ``ProviderAuthError`` on bad credentials and
    ``ProviderNotFoundError`` when Stripe reports a missing resource, keeping
    the HTTP layer provider-agnostic.
    """

    name = "stripe"

    def __init__(self, api_key: str, base_url: str = "") -> None:
        if not api_key:
            raise ProviderAuthError(
                "BILLING_API_KEY is required for provider=stripe"
            )
        import stripe  # lazy import

        stripe.api_key = api_key
        if base_url:
            stripe.api_base = base_url
        self._stripe = stripe
        # "test" for sk_test_... keys, "live" for sk_live_... keys.
        self._mode = "test" if api_key.startswith(("sk_test_", "rk_test_")) else "live"

    @staticmethod
    def _translate(exc: Exception) -> ProviderError:
        """Map a stripe library exception to a provider-error type."""
        # Imported lazily so this only runs on the Stripe path.
        import stripe as _s

        if isinstance(exc, _s.error.AuthenticationError):
            return ProviderAuthError(f"Stripe authentication failed: {exc}")
        if isinstance(exc, _s.error.InvalidRequestError):
            # InvalidRequestError is Stripe's signal for a missing resource
            # (e.g. customer_cus_X does not exist) or a bad parameter.
            return ProviderNotFoundError(f"Stripe request failed: {exc}")
        return ProviderError(f"Stripe error: {exc}")

    def _customer(self, obj) -> Customer:
        return Customer(
            id=obj["id"],
            email=obj.get("email", "") or "",
            name=obj.get("name", "") or "",
        )

    def create_customer(self, email: str, name: str = "") -> Customer:
        try:
            params: dict = {"email": email}
            if name:
                params["name"] = name
            return self._customer(self._stripe.Customer.create(**params))
        except Exception as exc:  # stripe.error.*
            raise self._translate(exc) from exc

    def get_customer(self, customer_id: str) -> Customer:
        try:
            return self._customer(self._stripe.Customer.retrieve(customer_id))
        except Exception as exc:
            raise self._translate(exc) from exc

    def create_invoice(
        self, customer_id: str, amount: int, currency: str = "usd",
        description: str = "",
    ) -> Invoice:
        try:
            # Draft invoice -> one line item -> finalize. This mirrors how a
            # single, discrete charge is represented in real Stripe billing.
            draft = self._stripe.Invoice.create(customer=customer_id)
            self._stripe.InvoiceItem.create(
                customer=customer_id,
                amount=amount,
                currency=currency,
                description=description or "charge",
                invoice=draft["id"],
            )
            finalized = self._stripe.Invoice.finalize_invoice(draft["id"])
            return Invoice(
                id=finalized["id"],
                customer_id=customer_id,
                amount=amount,
                currency=currency,
                status=finalized["status"],
                description=description,
            )
        except Exception as exc:
            raise self._translate(exc) from exc

    def charge(
        self, customer_id: str, amount: int, currency: str = "usd",
    ) -> PaymentIntent:
        try:
            pi = self._stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={"enabled": True},
            )
            return PaymentIntent(
                id=pi["id"],
                customer_id=customer_id,
                amount=amount,
                currency=currency,
                status=pi["status"],
            )
        except Exception as exc:
            raise self._translate(exc) from exc

    def health(self) -> dict:
        return {
            "provider": self.name,
            "status": "ok",
            "mode": self._mode,
        }


def build_provider(provider: str, api_key: str, base_url: str) -> BillingProvider:
    """Factory that returns the adapter for the configured provider."""
    provider = (provider or "stub").lower()
    if provider == "stub":
        return StubBillingProvider(base_url=base_url, api_key=api_key)
    if provider == "stripe":
        return StripeBillingProvider(api_key=api_key, base_url=base_url)
    if provider == "chargebee":
        from .chargebee import ChargebeeBillingProvider

        return ChargebeeBillingProvider(api_key=api_key, base_url=base_url)
    if provider == "paddle":
        from .paddle import PaddleBillingProvider

        return PaddleBillingProvider(api_key=api_key, base_url=base_url)
    raise ValueError(
        f"Unsupported BILLING_PROVIDER: {provider!r} "
        "(supported: stub, stripe, chargebee, paddle)"
    )

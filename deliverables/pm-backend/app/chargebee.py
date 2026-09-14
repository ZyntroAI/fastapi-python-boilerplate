"""Chargebee billing adapter.

A second real provider behind the same ``BillingProvider`` interface as the
Stripe adapter. Chargebee uses REST over the ``chargebee`` Python client;
here we call it via ``requests`` against the REST API so the adapter has no
extra hard dependency beyond the already-optional provider key.

Base URL form: https://<site>.chargebee.com/api/v2
Auth:            Basic <api_key> with an empty password (Chargebee convention)

Selected by setting BILLING_PROVIDER=chargebee.
"""
from __future__ import annotations

import base64

from .billing import (
    Customer,
    Invoice,
    PaymentIntent,
    ProviderAuthError,
    ProviderError,
    ProviderNotFoundError,
)


class ChargebeeBillingProvider:
    """Chargebee adapter implementing the provider-neutral billing interface."""

    name = "chargebee"

    def __init__(self, api_key: str, base_url: str = "") -> None:
        if not api_key:
            raise ProviderAuthError(
                "BILLING_API_KEY is required for provider=chargebee"
            )
        if not base_url:
            raise ProviderAuthError(
                "BILLING_BASE_URL (your Chargebee site, "
                "https://<site>.chargebee.com/api/v2) is required "
                "for provider=chargebee"
            )
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        # test vs live: Chargebee sites end in "-test" or "-live"
        self._mode = "test" if "-test" in base_url else "live"

    def _headers(self) -> dict:
        token = base64.b64encode(f"{self._api_key}:".encode()).decode()
        return {"Authorization": f"Basic {token}"}

    def _request(self, method: str, path: str, **kwargs) -> dict:
        import requests  # lazy import so the test layer can inject a fake

        try:
            resp = requests.request(
                method,
                f"{self._base_url}{path}",
                headers=self._headers(),
                timeout=30,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ProviderError(f"Chargebee request failed: {exc}") from exc

        if resp.status_code == 401:
            raise ProviderAuthError("Chargebee authentication failed")
        if resp.status_code == 404:
            raise ProviderNotFoundError(f"Chargebee resource not found: {path}")
        if not resp.ok:
            raise ProviderError(
                f"Chargebee error {resp.status_code}: {resp.text[:200]}"
            )
        return resp.json()

    def create_customer(self, email: str, name: str = "") -> Customer:
        payload = {"customer": {"email": email}}
        if name:
            payload["customer"]["first_name"] = name.split()[0]
            if len(name.split()) > 1:
                payload["customer"]["last_name"] = " ".join(name.split()[1:])
        data = self._request("POST", "/customers", json=payload)
        c = data["customer"]
        return Customer(
            id=c["id"],
            email=c.get("email", ""),
            name=f"{c.get('first_name','')} {c.get('last_name','')}".strip(),
        )

    def get_customer(self, customer_id: str) -> Customer:
        data = self._request("GET", f"/customers/{customer_id}")
        c = data["customer"]
        return Customer(
            id=c["id"],
            email=c.get("email", ""),
            name=f"{c.get('first_name','')} {c.get('last_name','')}".strip(),
        )

    def create_invoice(
        self, customer_id: str, amount: int, currency: str = "usd",
        description: str = "",
    ) -> Invoice:
        # Chargebee bills via a subscription/charge; the simplest standing
        # representation is an immediate one-off charge against the customer.
        payload = {
            "invoice": {
                "customer_id": customer_id,
                "currency_code": currency.upper(),
                "addons": [
                    {
                        "amount": amount / 100,  # Chargebee uses major units
                        "description": description or "charge",
                    }
                ],
            }
        }
        data = self._request("POST", "/invoices", json=payload)
        inv = data["invoice"]
        return Invoice(
            id=inv["id"],
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status=inv.get("status", "draft"),
            description=description,
        )

    def charge(
        self, customer_id: str, amount: int, currency: str = "usd",
    ) -> PaymentIntent:
        # Chargebee is subscription-led; a PaymentIntent equivalent is the
        # "payment intent" created against the customer's payment method.
        payload = {
            "payment_intent": {
                "customer_id": customer_id,
                "amount": amount / 100,
                "currency_code": currency.upper(),
            }
        }
        data = self._request("POST", "/payment_intents", json=payload)
        pi = data["payment_intent"]
        return PaymentIntent(
            id=pi["id"],
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status=pi.get("status", "inited"),
        )

    def health(self) -> dict:
        return {"provider": self.name, "status": "ok", "mode": self._mode}

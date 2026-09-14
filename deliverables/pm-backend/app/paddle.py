"""Paddle billing adapter.

A third real provider behind the same ``BillingProvider`` interface as the
Stripe and Chargebee adapters. Talks to the Paddle Billing API (v2) over
``requests`` (lazy-imported) so it adds no hard dependency unless selected.

Base URL:  https://api.paddle.com (live) / https://sandbox-api.paddle.com (sandbox)
Auth:      Authorization: Bearer <api_key>
Amounts:   Paddle Billing expects minor units as STRINGS (e.g. "2500").

Paddle is transaction-led: a *transaction* is the billable record, and an
invoice is generated from it. The adapter maps to the neutral interface as:
    create_invoice -> a manually-collected transaction (an invoice to send)
    charge         -> an automatically-collected transaction (an immediate charge)

Selected by setting BILLING_PROVIDER=paddle.
"""
from __future__ import annotations

from .billing import (
    Customer,
    Invoice,
    PaymentIntent,
    ProviderAuthError,
    ProviderError,
    ProviderNotFoundError,
)

_DEFAULT_BASE = "https://api.paddle.com"
_SANDBOX_BASE = "https://sandbox-api.paddle.com"


class PaddleBillingProvider:
    """Paddle Billing adapter implementing the neutral billing interface."""

    name = "paddle"

    def __init__(self, api_key: str, base_url: str = "") -> None:
        if not api_key:
            raise ProviderAuthError(
                "BILLING_API_KEY is required for provider=paddle"
            )
        self._api_key = api_key
        self._base_url = (base_url or _DEFAULT_BASE).rstrip("/")
        # Sandbox endpoints signal test mode.
        self._mode = "test" if "sandbox" in self._base_url else "live"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

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
            raise ProviderError(f"Paddle request failed: {exc}") from exc

        if resp.status_code == 401:
            raise ProviderAuthError("Paddle authentication failed")
        if resp.status_code == 404:
            raise ProviderNotFoundError(f"Paddle resource not found: {path}")
        if not resp.ok:
            raise ProviderError(
                f"Paddle error {resp.status_code}: {resp.text[:200]}"
            )

        body = resp.json()
        # Paddle wraps every payload in {"data": ...}.
        return body.get("data", body)

    def _customer(self, c: dict) -> Customer:
        return Customer(
            id=c.get("id", ""),
            email=c.get("email", "") or "",
            name=c.get("name", "") or "",
        )

    def create_customer(self, email: str, name: str = "") -> Customer:
        payload: dict = {"email": email}
        if name:
            payload["name"] = name
        return self._customer(self._request("POST", "/customers", json=payload))

    def get_customer(self, customer_id: str) -> Customer:
        return self._customer(self._request("GET", f"/customers/{customer_id}"))

    def _transaction(
        self, customer_id: str, amount: int, currency: str,
        description: str, collection_mode: str,
    ) -> dict:
        payload = {
            "customer_id": customer_id,
            "collection_mode": collection_mode,
            "items": [
                {
                    "quantity": 1,
                    "price": {
                        "description": description or "charge",
                        "unit_price": {
                            "amount": str(amount),  # minor units, as a string
                            "currency_code": currency.upper(),
                        },
                        "product": {
                            "name": description or "charge",
                            "tax_category": "standard",
                        },
                    },
                }
            ],
        }
        return self._request("POST", "/transactions", json=payload)

    def create_invoice(
        self, customer_id: str, amount: int, currency: str = "usd",
        description: str = "",
    ) -> Invoice:
        txn = self._transaction(
            customer_id, amount, currency, description, "manual"
        )
        return Invoice(
            id=txn.get("id", ""),
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status=txn.get("status", "draft"),
            description=description,
        )

    def charge(
        self, customer_id: str, amount: int, currency: str = "usd",
    ) -> PaymentIntent:
        txn = self._transaction(
            customer_id, amount, currency, "charge", "automatic"
        )
        return PaymentIntent(
            id=txn.get("id", ""),
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            status=txn.get("status", "ready"),
        )

    def health(self) -> dict:
        return {"provider": self.name, "status": "ok", "mode": self._mode}

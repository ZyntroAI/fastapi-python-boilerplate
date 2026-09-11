"""WhatsApp Cloud API notifier (Meta Graph API v18.0+).

Read-only helper for CI/CD alerts. No credentials in code — everything comes
from environment variables:
    WHATSAPP_TOKEN     Bearer token with whatsapp_business_messaging
    WHATSAPP_PHONE_ID  sender phone-number id (digits only)
    ADMIN_PHONE        recipient in international format, no '+' (e.g. 66812345678)
    WHATSAPP_API_VER   API version (default v18.0)
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

import requests

DEFAULT_API_VERSION = "v18.0"
GRAPH_BASE = "https://graph.facebook.com"


class WhatsAppConfigError(ValueError):
    """Raised when required environment configuration is missing."""


class WhatsAppClient:
    """Thin client for the WhatsApp Cloud API (send text messages)."""

    def __init__(
        self,
        token: Optional[str] = None,
        phone_id: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: float = 15.0,
    ) -> None:
        self.token = token or os.getenv("WHATSAPP_TOKEN", "")
        self.phone_id = phone_id or os.getenv("WHATSAPP_PHONE_ID", "")
        self.api_version = api_version or os.getenv("WHATSAPP_API_VER", DEFAULT_API_VERSION)
        self.timeout = timeout
        if not self.token or not self.phone_id:
            raise WhatsAppConfigError(
                "WHATSAPP_TOKEN and WHATSAPP_PHONE_ID must be set"
            )
        if not self.phone_id.isdigit():
            raise WhatsAppConfigError("WHATSAPP_PHONE_ID must be digits only")
        self.base_url = f"{GRAPH_BASE}/{self.api_version}/{self.phone_id}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def test_connection(self) -> Tuple[bool, Dict[str, Any]]:
        """GET the phone-number node to validate token/phone id.

        A well-formed config returns 200. Error code 100 / subcode 33
        ("Unsupported get request") means wrong URL, GET-vs-POST mixup, or
        a bad phone id — see docs/notifications/WHATSAPP.md.
        """
        try:
            resp = requests.get(self.base_url, headers=self.headers, timeout=self.timeout)
        except requests.RequestException as exc:
            return False, {"error": str(exc)}
        try:
            body = resp.json()
        except ValueError:
            body = {"raw": resp.text}
        return resp.status_code == 200, body

    def send_message(
        self, to: str, text: str, preview_url: bool = True
    ) -> Tuple[bool, str]:
        """POST a text message. Returns (ok, message_id_or_error)."""
        if not to:
            return False, "recipient phone is empty"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": text},
            "preview_url": preview_url,
        }
        try:
            resp = requests.post(
                f"{self.base_url}/messages",
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except requests.HTTPError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            return False, detail
        except requests.RequestException as exc:
            return False, str(exc)
        data = resp.json()
        msg_id = (data.get("messages") or [{}])[0].get("id", "unknown")
        return True, msg_id


def main() -> int:
    """CLI entry: verify connection then send a test message."""
    recipient = os.getenv("ADMIN_PHONE", "")
    try:
        client = WhatsAppClient()
    except WhatsAppConfigError as exc:
        print(f"configuration error: {exc}")
        return 2

    ok, info = client.test_connection()
    print(f"connection: {'ok' if ok else 'failed'} -> {info}")
    if not ok:
        return 1
    sent, detail = client.send_message(
        to=recipient, text="WhatsApp CI notification test - OK"
    )
    print(f"send: {'ok' if sent else 'failed'} -> {detail}")
    return 0 if sent else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

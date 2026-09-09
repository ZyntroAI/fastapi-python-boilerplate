"""Webhook service — ส่งผลงานพร้อมลายเซ็น HMAC-SHA256"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any, Optional

logger = logging.getLogger("webhook")

try:
    import httpx

    _HAS_HTTPX = True
except Exception:  # pragma: no cover
    _HAS_HTTPX = False


def sign_payload(payload: dict, secret: str) -> str:
    """คำนวณ HMAC-SHA256 จาก payload canonical JSON"""
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_signature(payload: dict, secret: str, signature: str) -> bool:
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, signature)


async def send_webhook(
    url: str,
    payload: dict,
    secret: Optional[str] = None,
    timeout: float = 10.0,
) -> bool:
    """ส่ง webhook พร้อม header X-Signature (HMAC-SHA256) ถ้ามี secret"""
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["X-Signature"] = sign_payload(payload, secret)
        headers["X-Signature-Algo"] = "sha256"
    if not _HAS_HTTPX:  # pragma: no cover
        logger.warning("httpx ไม่ได้ติดตั้ง — ข้าม webhook")
        return False
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            return resp.status_code < 300
    except Exception as exc:  # noqa: BLE001
        logger.warning("webhook ส่งล้มเหลว: %s", exc)
        return False

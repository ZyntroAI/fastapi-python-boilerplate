"""ห่อ firecrawl SDK v1.x — แคช Redis + retry อัตโนมัติ + fail-open"""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Optional

from app.config.settings import Settings

logger = logging.getLogger("firecrawl")

try:
    from firecrawl import FirecrawlApp

    _HAS_FIRECRAWL = True
except Exception:  # pragma: no cover
    _HAS_FIRECRAWL = False


def _cache_key(kind: str, payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"fc:{kind}:{digest}"


class FireCrawlService:
    """Service ครอบ SDK — ถ้า SDK/คีย์หาย หรือ FireCrawl ล่ม จะ fail-open (ไม่ crash)"""

    def __init__(self, settings: Settings, cache=None):
        self._settings = settings
        self._cache = cache  # RedisClient หรือ None
        self._client = None
        if _HAS_FIRECRAWL and settings.firecrawl_api_key:
            try:
                self._client = FirecrawlApp(
                    api_key=settings.firecrawl_api_key,
                    api_url=settings.firecrawl_base_url,
                )
            except Exception as exc:  # pragma: no cover
                logger.warning("Firecrawl client init failed: %s", exc)

    # ---------- scrape ----------
    async def scrape(self, url: str, options: Optional[dict] = None) -> dict:
        options = options or {}
        payload = {"url": url, **options}
        cache_key = _cache_key("scrape", payload)

        # 1) แคช
        if self._cache is not None:
            cached = await self._cache.get_json(cache_key)
            if cached is not None:
                return {**cached, "cache": "HIT"}

        result = await self._scrape_remote(url, options)

        # 2) เก็บแคช
        if self._cache is not None and result.get("success"):
            await self._cache.set_json(cache_key, result, self._settings.cache_ttl_scrape)

        return {**result, "cache": "MISS"}

    async def _scrape_remote(self, url: str, options: dict) -> dict:
        if self._client is None:
            # fail-open: คืนค่า degraded แทน crash
            return {"success": False, "error": "FireCrawl ไม่ได้ตั้งค่า (ไม่มี key)", "markdown": None, "metadata": None}
        last_err: Optional[Exception] = None
        for attempt in range(1, self._settings.firecrawl_retries + 1):
            try:
                res = self._client.scrape_url(url, params=options)
                if isinstance(res, dict) and res.get("success") is False:
                    # SDK บางรุ่น return dict
                    return {"success": False, "error": str(res.get("error", "unknown")), "markdown": None, "metadata": None}
                return {
                    "success": True,
                    "markdown": (res or {}).get("markdown") if isinstance(res, dict) else getattr(res, "markdown", None),
                    "metadata": (res or {}).get("metadata") if isinstance(res, dict) else getattr(res, "metadata", None),
                }
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                logger.warning("scrape attempt %s failed: %s", attempt, exc)
        return {"success": False, "error": str(last_err or "unknown"), "markdown": None, "metadata": None}

    # ---------- crawl (async ผ่าน Celery task) ----------
    async def crawl_async(self, url: str, options: Optional[dict] = None) -> str:
        """ส่งงาน crawl เข้าคิว Celery → return task_id (ไม่บล็อก)"""
        from app.workers.tasks import crawl_url_task  # import ช้า กัน circular

        options = options or {}
        return crawl_url_task.delay(url, options).id

    # ---------- job status ----------
    async def crawl_status(self, crawl_id: str) -> dict:
        if self._client is None:
            return {"status": "unknown", "error": "FireCrawl ไม่ได้ตั้งค่า", "data": None}
        try:
            res = self._client.check_crawl_status(crawl_id)
            return {
                "status": (res or {}).get("status", "unknown"),
                "data": (res or {}).get("data"),
                "error": (res or {}).get("error"),
            }
        except Exception as exc:  # pragma: no cover
            logger.warning("crawl status failed (fail-open): %s", exc)
            return {"status": "unknown", "error": str(exc), "data": None}


_service: Optional[FireCrawlService] = None


def get_firecrawl_service(settings: Settings, cache=None) -> FireCrawlService:
    global _service
    if _service is None:
        _service = FireCrawlService(settings, cache=cache)
    return _service

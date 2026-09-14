"""Celery tasks — งานเบื้องหลัง: crawl_url, scrape_url

ออกแบบให้ import ได้ทั้งแบบ async wrapper (dev/test) และ Celery task (production)
worker ใช้ firecrawl SDK v1.x แบบ sync ใน thread, ผลงานเก็บ Redis ให้ /tasks/{id} อ่าน
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Optional

from app.config.settings import get_settings
from app.core.redis import get_state_client

logger = logging.getLogger("worker")

TASK_KEY_PREFIX = "fc:task:"


def _task_key(task_id: str) -> str:
    return f"{TASK_KEY_PREFIX}{task_id}"


def _run_scrape_sync(url: str, options: Optional[dict]) -> dict:
    """รัน scrape จริงแบบ sync (ใน worker thread) — ใช้ SDK v1.x โดยตรง"""
    from app.core.firecrawl import FireCrawlService

    svc = FireCrawlService(get_settings())
    if svc._client is None:
        return {"success": False, "error": "FireCrawl ไม่ได้ตั้งค่า (ไม่มี key)", "data": None}
    try:
        res = svc._client.scrape_url(url, params=options or {})
        return {
            "success": True,
            "markdown": (res or {}).get("markdown") if isinstance(res, dict) else getattr(res, "markdown", None),
            "metadata": (res or {}).get("metadata") if isinstance(res, dict) else getattr(res, "metadata", None),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("scrape %s failed", url)
        return {"success": False, "error": str(exc), "markdown": None, "metadata": None}


def _run_crawl_sync(url: str, options: Optional[dict]) -> dict:
    """รัน crawl แบบ sync — SDK v1.x crawl_url"""
    from app.core.firecrawl import FireCrawlService

    svc = FireCrawlService(get_settings())
    if svc._client is None:
        return {"success": False, "error": "FireCrawl ไม่ได้ตั้งค่า (ไม่มี key)", "data": None}
    try:
        res = svc._client.crawl_url(url, params=options or {})
        return {"success": True, "data": res}
    except Exception as exc:  # noqa: BLE001
        logger.exception("crawl %s failed", url)
        return {"success": False, "error": str(exc), "data": None}


async def _store_result(task_id: str, result: dict, ttl: int = 1800) -> None:
    try:
        cache = get_state_client(get_settings())
        await cache.set_json(_task_key(task_id), result, ttl)
    except Exception as exc:  # pragma: no cover
        logger.warning("store result failed: %s", exc)


# ---------- async task (เรียกจาก API ใน process เดียว — dev/test) ----------
async def crawl_url(url: str, options: Optional[dict] = None) -> str:
    task_id = str(uuid.uuid4())
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _run_crawl_sync, url, options)
    await _store_result(task_id, {"status": "completed", **result})
    return task_id


async def scrape_url(url: str, options: Optional[dict] = None) -> str:
    task_id = str(uuid.uuid4())
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _run_scrape_sync, url, options)
    await _store_result(task_id, {"status": "completed", **result})
    return task_id


# ---------- Celery tasks (production: worker แยก, task_acks_late) ----------
try:
    from app.workers.celery import celery_app

    @celery_app.task(name="app.workers.tasks.crawl_url_task", bind=True, max_retries=3)
    def crawl_url_task(self, url: str, options: Optional[dict] = None):
        try:
            result = _run_crawl_sync(url, options)
            task_id = self.request.id or ""
            asyncio.run(_store_result(task_id, {"status": "completed", **result}))
            return result
        except Exception as exc:  # noqa: BLE001
            logger.exception("crawl task failed")
            raise self.retry(exc=exc, countdown=2 * (self.request.retries + 1))

    @celery_app.task(name="app.workers.tasks.scrape_url_task", bind=True, max_retries=3)
    def scrape_url_task(self, url: str, options: Optional[dict] = None):
        try:
            result = _run_scrape_sync(url, options)
            task_id = self.request.id or ""
            asyncio.run(_store_result(task_id, {"status": "completed", **result}))
            return result
        except Exception as exc:  # noqa: BLE001
            raise self.retry(exc=exc, countdown=2 * (self.request.retries + 1))

except Exception as exc:  # pragma: no cover
    logger.warning("Celery not configured, sync tasks unavailable: %s", exc)

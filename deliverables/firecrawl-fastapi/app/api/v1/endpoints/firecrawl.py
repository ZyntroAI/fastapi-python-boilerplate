"""API endpoints: /scrape, /crawl, /tasks/{id} — ล้วน async + fail-open"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.config.settings import Settings, get_settings
from app.core.redis import get_cache_client, get_state_client
from app.core.firecrawl import FireCrawlService
from app.schemas.firecrawl import (
    CrawlRequest,
    ScrapeRequest,
    ScrapeResponse,
    TaskResponse,
    TaskResult,
)
from app.workers import tasks

router = APIRouter(prefix="/firecrawl", tags=["firecrawl"])


def _service(settings: Settings = Depends(get_settings)) -> FireCrawlService:
    cache = get_cache_client(settings)
    return FireCrawlService(settings, cache=cache)


@router.post("/scrape", response_model=ScrapeResponse, status_code=200)
async def scrape(req: ScrapeRequest, svc: FireCrawlService = Depends(_service)):
    url = str(req.url)
    options = {
        "formats": req.formats,
        "onlyMainContent": req.only_main_content,
    }
    if req.wait_for:
        options["waitFor"] = req.wait_for
    if req.timeout:
        options["timeout"] = req.timeout

    result = await svc.scrape(url, options)
    if not result.get("success") and result.get("error"):
        # fail-open: คืน 200 พร้อม error (ไม่ crash) ตาม blueprint
        pass
    return ScrapeResponse(
        success=result.get("success", False),
        url=url,
        markdown=result.get("markdown"),
        metadata=result.get("metadata"),
        cache=result.get("cache", "MISS"),
        error=result.get("error"),
    )


@router.post("/crawl", response_model=TaskResponse, status_code=202)
async def crawl(req: CrawlRequest, settings: Settings = Depends(get_settings)):
    url = str(req.url)
    options = {
        "max_pages": req.max_pages,
        "ignore_sitemap": req.ignore_sitemap,
    }
    if req.webhook_url:
        options["webhook"] = str(req.webhook_url)

    task_id = await tasks.crawl_url(url, options)
    return TaskResponse(task_id=task_id, status="queued", url=url, max_pages=req.max_pages)


@router.get("/tasks/{task_id}", response_model=TaskResult)
async def task_status(task_id: str, settings: Settings = Depends(get_settings)):
    cache = get_state_client(settings)
    result = await cache.get_json(f"fc:task:{task_id}")
    if result is None:
        return TaskResult(task_id=task_id, status="not_found", data=None)
    return TaskResult(task_id=task_id, status=result.get("status", "unknown"), data=result.get("data"), error=result.get("error"))

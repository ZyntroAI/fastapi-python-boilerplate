"""Pydantic schemas — ตรวจสอบข้อมูลเข้า/ออก"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ScrapeRequest(BaseModel):
    url: HttpUrl
    formats: Optional[List[str]] = Field(default_factory=lambda: ["markdown"])
    only_main_content: bool = True
    wait_for: Optional[int] = Field(default=None, ge=0, le=60_000)
    timeout: Optional[int] = Field(default=None, ge=1_000, le=60_000)


class ScrapeResponse(BaseModel):
    success: bool
    url: str
    markdown: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    cache: str = "MISS"
    error: Optional[str] = None


class CrawlRequest(BaseModel):
    url: HttpUrl
    max_pages: int = Field(default=10, ge=1, le=1000)
    webhook_url: Optional[HttpUrl] = None
    ignore_sitemap: bool = False


class TaskResponse(BaseModel):
    task_id: str
    status: str = "queued"
    url: str
    max_pages: int = 10
    webhook_url: Optional[str] = None


class TaskResult(BaseModel):
    task_id: str
    status: str
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

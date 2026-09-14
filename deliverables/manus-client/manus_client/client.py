"""Manus REST API v2 client — async, provider-neutral, resilient.

Endpoint surface (ยืนยันจาก live probe ของ api.manus.ai):
    POST /v2/task.create         → สร้าง task
    GET  /v2/task.list           → รายการ tasks
    GET  /v2/task.listMessages   → ข้อความ/ผลลัพธ์ของ task
    POST /v2/task.stop           → หยุด task
    POST /v2/webhook.create      → ตั้ง webhook
    POST /v2/file.upload         → อัปโหลดไฟล์

Auth: ส่ง X-Manus-API-Key (หรือ Authorization: Bearer) — API รับทั้งคู่
Envelope: {"ok": bool, "request_id": str, ...}
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("manus_client")

DEFAULT_BASE = "https://api.manus.ai/v2"


class ManusAPIError(RuntimeError):
    """ข้อผิดพลาดจาก Manus API — มี code + request_id"""

    def __init__(self, message: str, code: str = "unknown", request_id: str = ""):
        super().__init__(message)
        self.code = code
        self.request_id = request_id


class ManusClient:
    def __init__(
        self,
        api_key: str = "",
        bearer_token: str = "",
        base_url: str = DEFAULT_BASE,
        timeout: float = 60.0,
    ):
        if not api_key and not bearer_token:
            raise ValueError("ต้องระบุ api_key หรือ bearer_token อย่างใดอย่างหนึ่ง")
        self._headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            self._headers["X-Manus-API-Key"] = api_key
        else:
            self._headers["Authorization"] = f"Bearer {bearer_token}"
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    # ---------- low-level ----------
    async def _request(self, method: str, path: str, json_body: Optional[dict] = None) -> Dict[str, Any]:
        url = f"{self._base}{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.request(method, url, headers=self._headers, json=json_body)
        try:
            data = resp.json()
        except ValueError:
            data = {"ok": False, "error": {"code": "bad_response", "message": resp.text[:200]}}
        # error envelope ของ Manus ใช้ ok:false + error:{code,message}
        if not data.get("ok", False) or resp.status_code >= 400:
            err = data.get("error", {})
            raise ManusAPIError(
                message=err.get("message", f"HTTP {resp.status_code}"),
                code=err.get("code", str(resp.status_code)),
                request_id=data.get("request_id", ""),
            )
        return data

    # ---------- task lifecycle ----------
    async def create_task(self, task: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        return await self._request("POST", "/task.create", {"task": task, "options": options or {}})

    async def list_tasks(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return await self._request("POST", "/task.list", {"limit": limit, "offset": offset})

    async def list_messages(self, task_id: str) -> Dict[str, Any]:
        return await self._request("POST", "/task.listMessages", {"taskId": task_id})

    async def stop_task(self, task_id: str) -> Dict[str, Any]:
        return await self._request("POST", "/task.stop", {"taskId": task_id})

    async def create_webhook(self, task_id: str, url: str) -> Dict[str, Any]:
        return await self._request("POST", "/webhook.create", {"taskId": task_id, "url": url})

    # ---------- polling helper ----------
    async def run_task(
        self,
        task: str,
        options: Optional[Dict] = None,
        interval: float = 2.0,
        max_wait: float = 600.0,
    ) -> Dict[str, Any]:
        """สร้าง task แล้ว poll จนจบ (สถานะที่ 'stopped'/'error') — คืนผลรวม"""
        created = await self.create_task(task, options)
        task_id = created.get("taskId") or created.get("task_id")
        if not task_id:
            raise ManusAPIError("response ไม่มี task_id", code="no_task_id", request_id=created.get("request_id", ""))

        deadline = time.time() + max_wait
        while time.time() < deadline:
            msgs = await self.list_messages(task_id)
            # หาสถานะจาก messages
            items = msgs.get("data") or msgs.get("messages") or []
            if items:
                statuses = {m.get("status") for m in items if isinstance(m, dict) and m.get("status")}
                if statuses & {"stopped", "error", "cancelled", "completed"}:
                    return msgs
            time.sleep(interval)

        raise ManusAPIError(f"task ยังไม่จบภายใน {max_wait}s", code="timeout", request_id="")

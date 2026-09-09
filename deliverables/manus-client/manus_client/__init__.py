"""manus_client — client สำหรับ Manus REST API v2 (task-first, dot-notation endpoints)

Surface นี้ยืนยันจาก live probe ของ api.manus.ai (ไม่ใช่จากเอกสารที่ยังไม่ verify):
  - Endpoint ใช้ dot-notation: /v2/task.create, /v2/task.list, /v2/task.listMessages
  - Auth รับ API Key หรือ Bearer Token (API ตอบ "require either API Key or Bearer Token")
  - Response envelope ใช้ `ok` (bool) + `request_id` (ไม่ใช่ `success`)
"""
from manus_client.client import ManusClient, ManusAPIError

__all__ = ["ManusClient", "ManusAPIError"]
__version__ = "0.1.0"

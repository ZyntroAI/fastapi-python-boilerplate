# manus-client — Manus REST API v2 client (โค้ดจริง)

Async client สำหรับ Manus REST API v2 แบบ **task-first** สร้างจาก **surface จริงที่ probe กับ `api.manus.ai`** ไม่ใช่จากเอกสารที่ยังไม่ verify

## Surface จริงที่ยืนยันจาก live probe

| รายการ | ความจริงที่ probe ได้ | เอกสารบางฉบับ (ไม่ตรง) |
|--------|----------------------|------------------------|
| Create task | `POST /v2/task.create` | `POST /v2/tasks` (404 — ไม่มีอยู่) |
| List tasks | `POST /v2/task.list` | `GET /v2/tasks` |
| Messages/result | `POST /v2/task.listMessages` | `GET /v2/tasks/{id}` |
| Stop | `POST /v2/task.stop` | `DELETE /v2/tasks/{id}` |
| Webhook | `POST /v2/webhook.create` | — |
| Auth | API Key **หรือ** Bearer Token | "X-Manus-API-Key เท่านั้น" (ผิด) |
| Envelope | `ok` + `request_id` + `error:{code,message}` | `success` (ผิด) |

## ไฟล์

- `manus_client/client.py` — `ManusClient` + `ManusAPIError` (async, httpx)
- `manus_client/cli.py` — CLI runner (สร้าง task → poll)
- `tests/test_client.py` — 10 tests แบบ mock (ไม่ใช้ key/network)
- `requirements.txt` — `httpx`

## ใช้งาน

```python
import asyncio
from manus_client.client import ManusClient

async def main():
    c = ManusClient(api_key="manus_...")  # หรือ bearer_token="..."
    result = await c.run_task(
        "ไปที่ https://example.com แล้วดึงข้อมูลสินค้า",
        options={"response_format": "json"},
    )
    print(result)

asyncio.run(main())
```

CLI:

```bash
export MANUS_API_KEY=manus_...
python -m manus_client.cli "งานที่อยากให้ทำ" --format json
```

## Test

```bash
pip install -r requirements.txt pytest
python -m pytest tests/ -q   # 10 passed
```

## หมายเหตุ

- รายละเอียด field ของ response (เช่น ชื่อ taskId/status จริง) อาจต่างจากที่คาดเล็กน้อย —
  client อ่าน `taskId`/`task_id` ทั้งคู่ และ `data`/`messages` ทั้งคู่ เพื่อกัน variation
- ต้องมี `MANUS_API_KEY` หรือ Bearer จริงเพื่อยืนยัน auth header ตัวสุดท้ายกับ live API

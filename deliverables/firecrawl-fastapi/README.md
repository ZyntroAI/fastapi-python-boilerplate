# FireCrawl + FastAPI

โปรเจกต์รวบรวมข้อมูลเว็บระดับโปรดักชัน: **scrape** หน้าเว็บ + **crawl** ลิงก์ลึก ผ่าน REST API
พร้อมคิวงานเบื้องหลัง (Celery), แคช Redis, rate-limit, webhook แบบ HMAC และ log โครงสร้าง

## สแตก

| ชิ้นส่วน | บทบาท |
|----------|--------|
| FastAPI | เว็บเฟรมเวิร์ก async |
| firecrawl-py **v1.x** | SDK (pin `<2.0.0` — surface `scrape_url`/`crawl_url`) |
| Redis | แคช + สถานะงาน + rate-limit |
| Celery | คิวงาน background (งานยาว) |
| structlog | log JSON |
| Docker | API + Worker + Redis |

## โครงสร้าง

```
app/
├── config/settings.py       # env + คอนฟิก (pydantic-settings)
├── core/
│   ├── firecrawl.py         # wrapper SDK + แคช + retry
│   ├── redis.py             # client fail-open
│   └── logging.py           # log JSON/console
├── api/v1/endpoints/firecrawl.py
├── schemas/firecrawl.py     # Pydantic
├── services/webhook.py      # HMAC-SHA256
├── middleware/rate_limit.py
└── workers/{celery,tasks}.py
```

## เริ่มใช้งาน

```bash
# local (dev)
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ใส่ FIRECRAWL_API_KEY
uvicorn main:app --reload

# หรือ Docker
docker compose up -d --build
```

## API

- `POST /api/v1/firecrawl/scrape` — ดึงหน้า (markdown/metadata), แคช Redis, `cache: HIT|MISS`
- `POST /api/v1/firecrawl/crawl` — ส่งงาน → `202 {task_id}`
- `GET /api/v1/firecrawl/tasks/{id}` — สถานะ/ผลงาน
- `GET /health` — สุขภาพระบบ

## คุณสมบัติ production

- **Fail-open**: ถ้า Redis/FireCrawl ล่ม → cache miss, rate-limiter ปล่อยผ่าน, task lookup 404 — แอปไม่ crash
- **Retry อัตโนมัติ** 3 ครั้ง (scrape) / `task_acks_late` + retry สำหรับ Celery
- **Cache key** จาก URL + options (SHA-256) → Redis TTL ตามประเภท
- **Webhook** ลงนาม HMAC-SHA256 ทุกครั้ง (`X-Signature`)
- **Rate limit** ต่อ IP: `/scrape` 120/นาที, `/crawl` 60/นาที
- **Log JSON** ผ่าน structlog

## Test

```bash
pip install pytest pytest-asyncio httpx
pytest tests/ -q   # ไม่ต้องใช้ service จริง (mock + fail-open path)
```

## หมายเหตุสำคัญ (SDK)

`firecrawl-py` มี 2 major version ที่ API ไม่เข้ากัน — โปรเจกต์ pin `<2.0.0` (v1.x) เพราะใช้
`scrape_url`/`crawl_url`/`check_crawl_status` อย่า upgrade ข้าม major โดยไม่ตรวจสอบ surface

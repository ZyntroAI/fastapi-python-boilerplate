# OnSpaceAI — Cost & Reliability Stack

FastAPI-based AI API infrastructure สำหรับ **low cost + high reliability + minimal token waste** ตาม blueprint ที่กำหนด

## Core Principle

> **Avoid the request before optimizing it.**
> Cache → Deduplicate → Compress Context → Budget Tokens → Fallback → Retry Only Safe

## โครงสร้าง

```
app/
├── config.py            # pydantic-settings จาก .env
├── middleware.py        # request-id + auth + metrics
├── cache.py             # Redis + hash key + TTL (fail-open) / MemoryCache
├── circuit_breaker.py   # Closed/Open/Half-Open
├── fallback_router.py   # Primary → Secondary → Degraded
├── metrics.py           # Prometheus counters/histograms
├── providers.py         # Provider contract + error model + retryable
├── context_compiler.py  # Trim/Dedup/Compress context
└── token_budget.py      # Cap/measure/save tokens
```

## เริ่มใช้งาน

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs  | Health: /health  | Metrics: /metrics
```

หรือ Docker: `docker compose up --build`

## Test

```bash
pytest -q   # 31 tests ผ่าน
```

## API

```bash
curl -X POST http://localhost:8000/api/ai \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain tokens","model":"gpt-4o","cache":true}'
```

ดูรายละเอียด: [TOKEN_OPTIMIZATION.md](TOKEN_OPTIMIZATION.md), [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)

## หมายเหตุ production

- ใช้ `MockProvider` เป็นค่าเริ่มต้น — ต่อ OpenAI/Anthropic จริงใน `providers.py` + ตั้ง key ใน `.env`
- Redis fail-open: ถ้า Redis ล่ม → cache miss (ไม่ crash)

# OnSpace Platform Integration

OnSpaceAI เดิมเป็น FastAPI app แยก (อยู่ที่ `deliverables/onspace-ai/`) — deliverable นี้คือ **ชั้นที่ดึง reliability engine ออกมาเป็น reusable service** เพื่อให้ ZyntroAI core เรียกใช้ได้จาก REST, GraphQL, worker, หรือ CLI โดยไม่ต้องมี HTTP

## แนวคิดหลัก

ไม่สร้าง AI engine ใหม่ — **ย้ายของเดิมทั้งดุ้น** แล้วเปลี่ยนสถานะจาก "แอป" เป็น "infrastructure service" ซึ่งเป็นข้อสรุปเดียวกับที่ตกลงกันไว้: OnSpaceAI ไม่ควรเป็น standalone FastAPI app อีกตัว แต่ควรเป็น AI infrastructure layer ที่มี projects → applications → generations → agents → deployments อยู่ด้านบน

```
Request
  ↓
OnSpaceAIService.generate()
  ↓
Context Compiler → Token Budget
  ↓
Cache (Redis / memory, fail-open)
  ↓
Circuit Breaker
  ↓
Provider chain: OpenAI → Anthropic → Google → Mock
  ↓
Response + Metrics
```

## โครงสร้าง

```
onspace-platform-integration/
├── onspace/
│   ├── service.py          # OnSpaceAIService — หัวใจ, ไม่มี FastAPI
│   ├── factory.py          # composition root (build_service)
│   ├── models.py           # AIRequest / AIResponse
│   ├── api.py              # thin HTTP routes
│   ├── app.py              # app factory + register_onspace()
│   ├── middleware.py       # request-id + optional api-key
│   ├── cache.py            # hash key + Redis/memory, fail-open
│   ├── circuit_breaker.py  # CLOSED / OPEN / HALF_OPEN
│   ├── context.py          # clean / dedup / trim / estimate
│   ├── token_budget.py     # per-model ceiling
│   ├── fallback.py         # FallbackRouter (+ route_with_meta)
│   ├── metrics.py          # Prometheus
│   ├── config.py           # ONSPACE_* settings
│   └── providers/          # base + openai + anthropic + google + mock
└── tests/                  # 58 tests
```

## วิธีใช้

### เป็น service (worker / CLI / GraphQL)

```python
from onspace import build_service, AIRequest

service = build_service()
response = await service.generate(AIRequest(prompt="hello", model="gpt-4o"))
print(response.content, response.provider, response.cached)
```

### ผูกเข้ากับ FastAPI core ที่มีอยู่

```python
from fastapi import FastAPI
from onspace.app import register_onspace

app = FastAPI()
register_onspace(app)   # เพิ่ม /api/v1/ai/generate + /api/v1/ai/health
```

### รันเดี่ยวเพื่อทดสอบ

```python
from onspace.app import create_onspace_app

app = create_onspace_app()   # เปิด /docs, /api/v1/ai/*, /metrics
```

## Configuration

ทุกค่าอ่านจาก env ด้วย prefix `ONSPACE_` — ไม่แตะ config ของ core app:

| ตัวแปร | ค่าเริ่มต้น | หมายเหตุ |
|---|---|---|
| `ONSPACE_OPENAI_API_KEY` | `""` | ถ้าว่าง provider จะไม่ถูก register |
| `ONSPACE_ANTHROPIC_API_KEY` | `""` | |
| `ONSPACE_GOOGLE_API_KEY` | `""` | |
| `ONSPACE_REDIS_URL` | `redis://localhost:6379/0` | ใช้เมื่อเรียก `build_redis_cache()` |
| `ONSPACE_CACHE_TTL` | `300` | วินาที |
| `ONSPACE_CIRCUIT_FAILURE_THRESHOLD` | `5` | |
| `ONSPACE_CIRCUIT_RECOVERY_SECONDS` | `30` | |
| `ONSPACE_API_KEY` | `""` | ถ้าตั้ง จะบังคับ `X-API-Key` |

**ไม่มี key เลย →** provider chain จะ fallback เป็น `MockProvider` เพื่อให้ local/dev รันได้ทันที

## Provider chain

ลำดับคือ **OpenAI → Anthropic → Google** ตามด้วย mock (เมื่อไม่มี key)

- retryable (408/429/502/503/504) → ลอง provider ถัดไป
- non-retryable (400/401/403/422) → **หยุดทันที** ไม่ลอยไปตัวอื่น (ประหยัด cost)
- circuit เปิด → ข้าม provider นั้น
- หมดทุกตัว → degraded (`AllProvidersUnavailable` → HTTP 503)

## Tests

```bash
pip install -r requirements.txt
pytest -q      # 58 passed
```

ชุดทดสอบแบ่งเป็น 5 ไฟล์:

| ไฟล์ | ครอบคลุม |
|---|---|
| `test_service.py` | service layer: generate, cache, budget, degraded, fallback |
| `test_primitives.py` | cache / circuit breaker / context / budget / router / error model |
| `test_http.py` | routes, status codes, `/metrics` |
| `test_factory.py` | provider ordering + settings wiring |
| `test_architecture.py` | **guard**: service ต้องไม่ import FastAPI |

`test_architecture.py` เป็นด่านกันถอยหลัง — ถ้ามีคนเผลอเอา FastAPI import เข้า `service.py` หรือยัด business logic กลับเข้า route, test จะ fail ทันที

## ความสัมพันธ์กับ `deliverables/onspace-ai/`

| | onspace-ai (เดิม) | onspace-platform-integration (ใหม่) |
|---|---|---|
| สถานะ | standalone app / reference | reusable service layer |
| import | ผูกกับ FastAPI app โดยตรง | service ไม่รู้จัก HTTP |
| providers | mock (+ TODO) | base + openai + anthropic + google + mock |
| ลำดับ provider | fix 2 ตัว | config-driven |
| error type | `HTTPException` ใน route | service โยน typed exception, route แปลเป็น HTTP |

`deliverables/onspace-ai/` **ยังอยู่ครบ** เป็น migration source / reference — ตามแผนยังไม่ลบจนกว่า integration tests จะผ่านครบฝั่ง core

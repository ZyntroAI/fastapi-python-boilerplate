# Migration Plan — OnSpaceAI → Platform Service

แผน 8 ขั้นจาก architecture ที่ตกลงกันไว้ ระบุว่าขั้นไหน **ทำแล้ว** ใน deliverable นี้ และขั้นไหน **ยังค้าง** เพราะต้องแตะ repo ส่วนอื่น

สถานะรวม: **Step 1–3 เสร็จ** (deliverable นี้) · Step 4–8 ค้าง (ต้องตัดสินใจ/แตะ `app/` core)

---

## Step 1 — Freeze existing deliverable ✅

`deliverables/onspace-ai/` ถูก freeze เป็น baseline/reference แล้ว — ยังรันได้ 31/31 tests ไม่ถูกแก้แม้แต่บรรทัดเดียว

## Step 2 — Extract shared services ✅

ย้าย reliability engine เป็น `onspace/` package (15 โมดูล) โดย**ไม่เขียน logic ใหม่**:

| เดิม (`onspace-ai/app/`) | ใหม่ (`onspace/`) | หมายเหตุ |
|---|---|---|
| `cache.py` | `cache.py` | เหมือนเดิม |
| `circuit_breaker.py` | `circuit_breaker.py` | เหมือนเดิม |
| `context_compiler.py` | `context.py` | ตัด `_` ในชื่อให้สั้นลง |
| `token_budget.py` | `token_budget.py` | import จาก `.context` แทน `app.context_compiler` |
| `fallback_router.py` | `fallback.py` | เพิ่ม `route_with_meta()` คืนชื่อ provider |
| `providers.py` | `providers/` | แยกเป็น package: base / openai / anthropic / google / mock |
| `metrics.py` | `metrics.py` | เหมือนเดิม |
| `middleware.py` | `middleware.py` | `AuthMiddleware` → `OnSpaceAuthMiddleware` |
| `config.py` | `config.py` | เปลี่ยนเป็น `ONSPACE_*` prefix + `get_onspace_settings()` |
| `main.py` (routes) | `api.py` + `app.py` | แยกรoute ออกจาก app factory |

## Step 3 — Introduce service layer ✅

`OnSpaceAIService` เป็น async service ที่ **ไม่มี FastAPI import** — เป็นข้อเรียกร้องหลักของ migration (test ใน `test_architecture.py` บังคับไว้)

Route เป็น thin layer:

```python
@router.post("/generate", response_model=AIResponse)
async def generate(request: AIRequest, service = Depends(get_onspace_service)):
    try:
        return await service.generate(request)
    except PayloadTooLarge as exc:
        raise HTTPException(413, f"payload too large: {exc.message}")
    except AllProvidersUnavailable as exc:
        raise HTTPException(503, exc.message)
```

เพิ่ม `factory.py` เป็น composition root เดียว — REST/GraphQL/worker/CLI ใช้ `build_service()` ตัวเดียวกัน

---

## Step 4 — Connect auth/config/Redis ⏳ ค้าง

**ค้างเพราะต้องตัดสินใจ ไม่ใช่เพราะทำไม่ได้**

- `app/core/config.py` เป็น OAuth2 PKCE app ที่มี **field บังคับ** (`OAUTH_CLIENT_ID`) — ถ้าให้ onspace import settings ตัวนี้ จะพังเมื่อรัน worker/CLI ที่ไม่มี OAuth env
- ทางออกที่เสนอ: ให้ onspace คง `ONSPACE_*` แยกไว้ แล้ว core app ค่อย**ฉีดค่า** เข้า `build_service(settings=...)` ตอน bootstrap
- Redis: `build_redis_cache()` พร้อมแล้ว แต่ยังไม่ได้ต่อเข้า core lifespan

## Step 5 — Add database modules ⏳ ค้าง

`projects / applications / generations / deployments` ยังไม่มี — **และไม่ควรสร้างเป็น `modules/`** ตามที่แผนสมมติ เพราะ repo นี้ไม่มี `modules/` จริง

repo ใช้ **`deliverables/<suite>/`** เป็น convention หลัก (มี 19 deliverable) ส่วน `app/` เป็น core app โครงสร้างที่ควรใช้คือ **vertical slice per module**:

```
app/modules_generations/
├── models.py     schemas.py     crud.py
├── service.py    routes.py
```

**ยังต้องตัดสินใจ**: จะเริ่มที่ module ไหน (แนะนำ `generations` เพราะผูกกับ AI service ตรงที่สุด)

## Step 6 — Connect Agent Runtime ⏳ ค้าง

Planner / Builder / Tester / Reviewer / Deployer — วางบน `OnSpaceAIService` ได้ทันที (เป็นเหตุผลที่ Step 3 ต้องมาก่อน) แต่ยังไม่มี agent code ใน repo

## Step 7 — Connect React Builder ⏳ ค้าง

`frontend/` มีอยู่จริง (React + Vite + TS) แต่เป็น OAuth demo shell — ยังไม่มี `builder/` (Canvas / ComponentTree / PropertiesPanel) ต้องสร้างใหม่

## Step 8 — Remove duplicated legacy ⏳ ค้าง (โดยเจตนา)

`deliverables/onspace-ai/` **ไม่ลบ** จนกว่า integration tests ฝั่ง core จะผ่าน — ตามแผนเดิม

---

## พร้อม merge ได้แล้ว

`deliverables/onspace-platform-integration/` เป็นไปตาม convention ของ repo, import ได้เอง ไม่พึ่ง `app/__init__.py`, และมี 58 tests ผ่าน

## Blocker ที่พบระหว่างทาง (ต้องแก้ก่อน Step 4)

`app/__init__.py` ที่ root **พังอยู่แล้ว** บน `main`:

```python
# ... import ...
FastAPIInstrumentor.instrument_app(app)   # ← ใช้ `app` ก่อนที่ FastAPI(...) จะถูกสร้าง ด้านล่าง
SQLAlchemyInstrumentor().instrument()      # ← instrument ทุก engine ที่ import
```

ผลคือ import `app` ไม่ได้เลย (ไม่ใช่แค่ onspace) และ `opentelemetry`/`slowapi` **ไม่มีใน `requirements.txt`** ที่ root — CI ที่รัน `pytest tests/` จะตายตั้งแต่ conftest

นี่ไม่ใช่ผลจาก migration นี้ (มีมาก่อน) แต่ **Step 4 จะทำต่อไม่ได้จนกว่าจะแก้** เพราะ Step 4 คือการให้ core app import onspace ซึ่งต้องผ่าน `app/__init__.py`

**ต้องตัดสินใจ**: แก้ `app/__init__.py` เอง หรือย้าย OnSpaceAI ไปเป็น package นอก namespace `app/` (ชื่อ `onspace` แบบ deliverable นี้) แล้วให้ core app เป็นฝ่าย import เข้ามา — แนวหลังปลอดภัยกว่าและเป็นสิ่งที่ deliverable นี้ทำไว้แล้ว

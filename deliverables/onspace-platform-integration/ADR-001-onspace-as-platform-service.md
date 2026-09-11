# ADR-001 — OnSpaceAI เป็น AI Infrastructure Layer ไม่ใช่ Standalone App

**Status:** Accepted
**Date:** 2026-09-11
**Deciders:** Nattapong Pornlumfah (ZyntroAI)

---

## บริบท (Context)

`deliverables/onspace-ai/` มี reliability engine ที่ทำงานได้จริง — cache, circuit breaker, fallback router, context compiler, token budget, Prometheus metrics — พร้อม 31 tests ผ่าน แต่ทั้งชุดถูกผูกเป็น **standalone FastAPI app** โดยมี business logic (การอ่าน cache / เช็ค budget / เรียก router) อยู่ใน route handler โดยตรง

ขณะเดียวกัน ZyntroAI core (`app/`) มี projects/applications/generations ที่ต้องเรียก LLM และต้องการ reliability pattern ชุดเดียวกัน

## ปัญหา (Problem)

ถ้าเก็บ OnSpaceAI เป็นแอปแยก:

1. **Duplicate logic** — ถ้าอยากได้ retry/cache/token optimization ใน core ต้องเขียนซ้ำหรือเรียกข้าม service ผ่าน HTTP
2. **ผูกกับ transport** — logic อยู่ใน route → เรียกจาก GraphQL resolver หรือ background worker ไม่ได้
3. **หลาย Redis client** — แอปแยกต้องมี Redis client ของตัวเอง ซ้ำกับ core infrastructure
4. **Auth ซ้อน** — แอปแยกต้องมี auth layer ของตัวเอง ซ้อนกับ OAuth2 PKCE ที่ core มีอยู่แล้ว

## ทางเลือกที่พิจารณา (Options)

| ทางเลือก | สรุป |
|---|---|
| **A. คงเป็น standalone app** | เรียกผ่าน HTTP ข้าม service · เสี่ยง duplicate Redis/auth/logic |
| **B. ยุบเข้า core โดยให้ route เรียก engine ตรง ๆ** | เร็ว แต่คงปัญหา transport coupling ไว้ |
| **C. ดึง engine เป็น reusable service แล้วให้ core import** | ✅ เลือกทางนี้ |

## การตัดสินใจ (Decision)

OnSpaceAI กลายเป็น **AI infrastructure/service layer** ที่ core import ได้ โดย:

- `OnSpaceAIService` เป็น async service ที่ **ไม่มี FastAPI import** — พิสูจน์และบังคับด้วย `test_architecture.py`
- Route เป็น thin layer: รับ request → เรียก service → แปล typed exception เป็น HTTP status
- `factory.py` เป็น composition root เดียว — REST / GraphQL / worker / CLI ใช้ `build_service()` ตัวเดียวกัน
- Config แยกด้วย prefix `ONSPACE_*` — ไม่อ่าน `app/core/config.py` (ซึ่งมี OAuth field บังคับ) เพื่อให้ worker/CLI รันได้โดยไม่มี OAuth env
- Provider chain เป็น config-driven: OpenAI → Anthropic → Google → mock
- `deliverables/onspace-ai/` **ไม่ลบ** — freeze เป็น reference จนกว่า core integration tests จะผ่าน

```
                 React Builder
                       │
                REST / GraphQL
                       │
                FastAPI Core (app/)
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Projects      Applications    Deployments
        └──────────────┼──────────────┘
                       ▼
              OnSpaceAIService          ← ชั้นนี้คือสิ่งที่ deliverable นี้ส่งมอบ
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      Cache      Token Budget   Circuit Breaker
        └──────────────┼──────────────┘
                       ▼
             Providers (OpenAI → Anthropic → Google)
```

## ผลที่ตามมา (Consequences)

**ด้านบวก**
- เขียน reliability logic ครั้งเดียว ใช้ได้ทุก transport
- ทดสอบ service ได้โดยไม่ต้องมี HTTP (58 tests, 45 ตัวไม่แตะ HTTP เลย)
- เพิ่ม provider ใหม่ = เพิ่มไฟล์เดียว ไม่แตะ router
- ลด Redis client ซ้ำได้ในอนาคต (Step 4)

**ด้านลบ / ต้นทุน**
- มีสองชุดชั่วคราว (`onspace-ai/` เดิม + `onspace/` ใหม่) จนกว่า Step 8 จะลบ
- ต้องตัดสินใจเรื่องที่วาง package ใหม่ — **ไม่ควรอยู่ใต้ `app/`** เพราะ `app/__init__.py` ที่ root พังอยู่แล้ว (ดู MIGRATION.md)

**ความเสี่ยงที่ค้าง**
- Step 4–8 ยังไม่ทำ — การต่อเข้า core จริงต้องแก้ `app/__init__.py` ก่อน
- ยังไม่มี database modules (`projects` / `applications` / `generations`)
- ยังไม่มี agent runtime (Planner / Builder / Tester / Reviewer / Deployer)

## เกณฑ์ทบทวน (Review Trigger)

ทบทวน ADR นี้เมื่อ:
- Step 4–8 เสร็จครบ (ควรยุบ `onspace-ai/` เดิมทิ้ง)
- มี transport ที่สอง (GraphQL) เรียก service จริง — ยืนยันว่า abstraction คุ้ม
- จำนวน provider เกิน 5 ราย — ทบทวนเรื่อง dynamic registration / plugin

# ✅ Task List — FastAPI + OnSpace.AI

ติดตามงานตาม [ROADMAP.md](./ROADMAP.md) — ติ๊กเมื่อทำเสร็จและมีหลักฐาน
ความรู้และตัวอย่างโค้ด: [docs/onspace-fastapi-knowledge-base.md](./docs/onspace-fastapi-knowledge-base.md)

---

## 🧪 Phase 0 — Baseline (PR #197 ปิดแล้ว)

- [x] PR #197 พร้อม
- [x] Merge (Squash) → `main` (2026-09-11 09:04 UTC)
- [x] ตรวจสอบ `onspace/` อิสระ (service ไม่มี FastAPI import)
- [x] 58 ทดสอบผ่าน (`deliverables/onspace-platform-integration/`)
- [ ] Tag `baseline-v1.0`
- [ ] ตัดสินใจเรื่อง `deliverables/onspace-ai/` (คงสภาพ / แช่แข็ง)

## 🛠️ Phase 1 — FastAPI Core

- [ ] แก้ `app/__init__.py` (import `app` ได้ — ดู PR #198)
- [ ] ย้าย `on_event("startup"/"shutdown")` → lifespan
- [ ] จัดการ dependencies (`bcrypt==4.0.1` + `passlib`)
- [ ] เปิด `/health` → 200 OK
- [ ] เปิด `/metrics`
- [ ] รันทดสอบทั้งหมดผ่าน

## 🔗 Phase 2 — Service

- [ ] เพิ่ม API Router (`/api/v1/ai/`)
- [ ] 3 Endpoints ครบ (`generations`, `generations/{id}`, `providers`)
- [ ] ตรวจสอบขอบเขต: Router → App Service → `OnSpaceAIService` → Factory เท่านั้น

## 📐 Phase 3 — Spec

- [ ] `ApplicationSpec` ฉบับเต็ม (Pydantic v2)
- [ ] Schema Contract กลาง
- [ ] กฎ: ห้าม LLM เขียนไฟล์จริงโดยตรง

## ⚙️ Phase 4 — Pipeline

- [ ] สถานะครบ (`pending → running → done → failed`)
- [ ] Background Worker (ไม่บล็อก HTTP)
- [ ] Query สถานะย้อนหลังได้

## 🤖 Phase 5 — Agent

- [ ] ใช้ Service Layer ร่วม (`OnSpaceAIService`)
- [ ] Provider / Cache / Retry กลาง — ไม่ทำซ้ำ

## 🎨 Phase 6 — Builder

- [ ] ยืนยันว่า Builder เป็นฟีเจอร์ใหม่ ไม่ทับ OAuth/สาธิตเดิม

## 🔒 Phase 7 — CI/CD

- [ ] SHA-pin workflows (11 actions — ดูรายการใน ROADMAP)
- [ ] แก้ `scan` job ที่ pin ไปยัง SHA ซึ่ง resolve ไม่ได้
- [ ] PR ความปลอดภัยแยกจากฟีเจอร์
- [ ] ขอสิทธิ์ `workflows` สำหรับ automation App (ถ้าจะ push เอง)

> 🔴 **ตรวจเมื่อ 2026-09-11:** CI ล้มทุก job ที่ *Set up job* —
> `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`
> ไม่ถูก pin เป็น SHA เต็ม (Analyze (python) และ Analyze (javascript-typescript) ผ่าน
> เพราะ pin แล้ว) → บล็อกทุก PR บน `main`

## 🚀 Phase 8 — Deploy

- [ ] Staging
- [ ] Production

---

🎯 **เป้าหมาย:** M4 Completed — `FastAPI + OnSpaceAI Integrated`

## Supply Chain Security

- [x] Pin every GitHub Action to a full commit SHA
- [x] Add `verify-sha` CI gate (blocks tags and branches)
- [x] Add `pin_workflows.py` updater
- [x] Document the policy and pin history in `SECURITY.md`
- [ ] Enable required status checks (`verify-sha`, `lint`, `test`) in repo settings
- [ ] Secret scanning for workflow files
- [ ] YAML linting for workflow structure

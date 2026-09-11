# 🚀 OnSpace.AI × ZyntroAI — FastAPI Boilerplate Roadmap

**Core Principle:** `Merge → Stabilize → Integrate → Build`

> **ห้ามข้ามรากฐาน** — เสถียรก่อนขยาย
> Stabilize the foundation before expanding scope.

This document is the single plan of record for integrating the **OnSpace.AI** platform
service into the `fastapi-python-boilerplate` app core. Task-level tracking lives in
[TASKS.md](./TASKS.md).

---

## 🧪 Phase 0 — ปิดงานปัจจุบัน (Baseline)

**ขั้นตอน:** PR #197 → Merge (Squash) → `main` → Tag: `baseline-v1.0`

### ✅ เกณฑ์ผ่าน

| เกณฑ์ | สถานะ | หลักฐาน |
| --- | --- | --- |
| PR #197 merged เข้า `main` | ✅ | merged 2026-09-11 09:04 UTC (`feat(onspace): extract OnSpaceAI engine into reusable platform service`) |
| `OnSpaceAIService` ไม่ผูก FastAPI | ✅ | `onspace/service.py` ไม่มี FastAPI import — REST/GraphQL/worker/CLI เรียก `generate()` ตัวเดียวกัน |
| ผ่าน **58 ทดสอบ** | ✅ | `deliverables/onspace-platform-integration/` — `58 passed` |
| แพ็กเกจ `onspace/` เป็นอิสระ | ✅ | ห่อ dependency เฉพาะที่ `onspace/api.py`, `onspace/app.py`, `onspace/middleware.py` (optional extras) |
| เอกสาร `ADR/` + `MIGRATION.md` ครบ | ✅ | `ADR-001-onspace-as-platform-service.md`, `MIGRATION.md` |
| Tag `baseline-v1.0` | ⬜ | ยังไม่ติด tag (repo มี tag ล่าสุด `v1.1.0`) |

**หมายเหตุ:** `deliverables/onspace-ai/` คือแอปต้นทางที่ยังทำงานอยู่ — คงสภาพเดิมไว้
(ไม่ freeze การแก้ใน PR นี้) ส่วน service ที่แยกออกมาอยู่ที่
`deliverables/onspace-platform-integration/onspace/`

---

## 🛠️ Phase 1 — ซ่อมแก่น FastAPI (สำคัญที่สุด)

**เป้าหมาย:** แก้การเริ่มทำงาน / import / สุขภาพของแอป — **ไม่รีแฟกเตอร์ใหญ่**

```
app/__init__.py → Startup → OpenTelemetry → SlowAPI → /health → /metrics
```

### สภาพที่ตรวจพบ (2026-09-11)

- `app/__init__.py` เรียก `FastAPIInstrumentor.instrument_app(app)` **ก่อน** ที่ `app`
  จะถูกสร้าง → `NameError: name 'app' is not defined` ทำให้ import `app` ไม่ได้
- มี `@app.on_event("startup"/"shutdown")` ซึ่ง deprecated (ควรย้ายไป lifespan)
- PR #198 (`fix(app): make the app package importable`) เปิดอยู่และแก้จุดนี้

### 📋 รายการตรวจ

- [ ] Import ถูกต้อง (`import app` ไม่ error)
- [ ] FastAPI เริ่มสะอาด (ไม่มี `NameError` / deprecation warning ที่ทำให้ startup พัง)
- [ ] Dependencies ไม่ขัดแย้ง (โดยเฉพาะ `bcrypt==4.0.1` คู่กับ `passlib`)
- [ ] `/health` → 200 OK
- [ ] `/metrics` ทำงาน
- [ ] ทดสอบทั้งหมดผ่าน

---

## 🔗 Phase 2 — เชื่อม OnSpace Service

**ขอบเขตสถาปัตยกรรม:**

```
FastAPI → Router → App Service → OnSpaceAIService → Provider Factory
```

### 📡 API Endpoints

| Method | Path | หน้าที่ |
| --- | --- | --- |
| `POST` | `/api/v1/ai/generations` | สร้างคำขอ |
| `GET` | `/api/v1/ai/generations/{id}` | ตรวจสอบสถานะ |
| `GET` | `/api/v1/ai/providers` | รายการผู้ให้บริการ |

**กฎเขตแดน:** Router ห้ามเรียก provider ตรง ๆ — ต้องผ่าน `OnSpaceAIService`
และ service ห้าม import อะไรจาก `app/`

---

## 📐 Phase 3 — โมเดลแอปพลิเคชัน

- กำหนด **`ApplicationSpec` ที่เสถียร** (Pydantic v2 model + schema กลาง)
- **กฎ:** ห้าม LLM เขียนไฟล์จริงโดยตรง — ต้องผ่าน spec ที่ validate แล้ว
- ใช้เป็นสัญญากลาง (contract) ทุกส่วน ทั้ง REST, GraphQL และ worker

---

## ⚙️ Phase 4 — ท่อประมวลผล

- สถานะ: `pending → running → done → failed`
- **งานยาว:** ใช้ Worker แยก (ไม่บล็อก HTTP request)
- เก็บ state ที่ query ได้ เพื่อรองรับ `GET /api/v1/ai/generations/{id}`

---

## 🤖 Phase 5 — ชั้น Agent

- เริ่ม **หลัง pipeline เสถียร**
- ทุกตัวใช้ **Service Layer เดียวกัน** (`OnSpaceAIService`)
- ❌ ไม่ทำซ้ำ provider / cache / retry ที่มีอยู่แล้ว

---

## 🎨 Phase 6 — Frontend Builder

- ปัจจุบัน: OAuth/สาธิต (`frontend/` React + Vite + TypeScript)
- Builder = **ฟีเจอร์ใหม่** — ไม่แปลงเปลือกเดิม

---

## 🔒 Phase 7 — CI/CD ความปลอดภัย

- **SHA-pinning** ทุก workflow action (ดูรายการด้านล่าง)
- PR แยกเฉพาะโครงสร้างพื้นฐาน — ไม่ปนกับฟีเจอร์

### action ที่ต้อง pin (ตรวจเมื่อ 2026-09-11)

`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`,
`actions/configure-pages@v5`, `actions/upload-pages-artifact@v3`,
`actions/deploy-pages@v5`, `codecov/codecov-action@v4`,
`gitleaks/gitleaks-action@v2`, `github/codeql-action/upload-sarif@v3`,
`dependabot/fetch-metadata@v2`, `pascalgn/automerge-action@v0.16.4`

**หมายเหตุ:** การแก้ไฟล์ `.github/workflows/` ต้องใช้สิทธิ์ `workflows` ซึ่ง automation
App ยังไม่มี — ต้องทำ PR นี้ด้วยมือหรือให้เจ้าของ repo push

---

## 🚀 Phase 8 — ปรับใช้งาน

- หลัง CI/CD & Security ผ่าน
- Deploy staging → production
- เปิด observability (OpenTelemetry + Prometheus `/metrics`) บนสภาพจริง

---

## 🎯 Milestone M4 — เสร็จสิ้นหลัก

**สถานะ:** `FastAPI + OnSpaceAI Integrated`

### 💡 คำแนะนำ

**หยุดที่ M4 ก่อนสร้าง Agent/Builder**

ทำให้ขอบเขต `FastAPI ↔ OnSpaceAI` มั่นคงก่อน — ลดความเสี่ยงที่ข้อผิดพลาดจะลาม
เข้าไปในชั้นที่สูงกว่าและหา root cause ได้ยาก

---

## 📎 ข้อมูล

- **Repo:** `ZyntroAI/fastapi-python-boilerplate`
- **Service package:** `deliverables/onspace-platform-integration/`
- **Source app:** `deliverables/onspace-ai/`
- **แผนงานที่เกี่ยวข้อง:** [TASKS.md](./TASKS.md)

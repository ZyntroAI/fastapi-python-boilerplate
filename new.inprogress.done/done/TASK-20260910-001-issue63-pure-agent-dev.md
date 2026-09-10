---
id: TASK-20260910-001
title: ปิด Issue #63 — pure-agent-dev reference implementation
status: done
priority: high
created: 2026-09-10
updated: 2026-09-10
owner: fig-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue: 63
prs: [169, 170]
blocked_by:
tokens: 48200
---

# TASK-20260910-001 — ปิด Issue #63

## เป้าหมาย

Issue #63 ("pure-agent-dev") ขอโครง Agent บน FastAPI ที่ไม่ผูกกับคลาวด์รายใดรายหนึ่ง พร้อมกฎว่าชั้น Agent ต้องไม่แตะ SDK ของ BytePlus

## งานที่ทำ

- [x] อ่าน Code Guide ฉบับเต็มใน Issue #63 (body + คอมเมนต์ 8 ฉบับ) แล้วแยกข้อกำหนดออกมาเป็นรายการ
- [x] สร้าง `pure_agent/` แยกชั้น providers / agents / services / schemas / api
- [x] ทำ `ComputeProvider` (ABC) + `MockComputeProvider` + BytePlus ECS adapter
- [x] แยก `planner.py` (คำสั่ง → AgentTask) กับ `executor.py` (AgentTask → provider)
- [x] เลือก provider ด้วย env `COMPUTE_PROVIDER` ที่ `api/deps.py` จุดเดียว
- [x] เขียน JSON Schema ภายนอก + Pydantic model แล้วมี test เทียบกันสองทาง
- [x] เขียน `tests/test_architecture.py` เดิน import graph จริง บังคับกฎ "Agent ห้าม import byteplus"
- [x] เขียน Dockerfile + docker-compose + pyproject + CI workflow ประจำ deliverable
- [x] รัน `pytest` 47/47 (ทั้งโหมดปกติและ `-O`) + `ruff` clean
- [x] เปิด PR #169 แล้ว merge (squash `590b8615`) → Issue ปิดอัตโนมัติ
- [x] เปิด PR #170 อัปเดต CHANGELOG แล้ว merge (squash `3ff8da60`)

## ไฟล์ที่ถูกแก้

| ไฟล์ | การเปลี่ยนแปลง |
| --- | --- |
| `deliverables/pure-agent-dev/pure_agent/providers/base.py` | สร้างใหม่ — `ComputeProvider` ABC |
| `deliverables/pure-agent-dev/pure_agent/providers/mock.py` | สร้างใหม่ — provider ในหน่วยความจำ |
| `deliverables/pure-agent-dev/pure_agent/providers/byteplus/ecs.py` | สร้างใหม่ — adapter (SDK call เป็น `TODO(byteplus)`) |
| `deliverables/pure-agent-dev/pure_agent/agents/planner.py` | สร้างใหม่ |
| `deliverables/pure-agent-dev/pure_agent/agents/executor.py` | สร้างใหม่ — เปลี่ยน `assert` เป็น `raise` หลัง test จับได้ |
| `deliverables/pure-agent-dev/pure_agent/api/deps.py` | สร้างใหม่ — จุดเลือก provider จุดเดียว |
| `deliverables/pure-agent-dev/schemas/agent-task.schema.json` | สร้างใหม่ — สัญญาภายนอก |
| `deliverables/pure-agent-dev/tests/test_architecture.py` | สร้างใหม่ — guard กฎสถาปัตยกรรม |
| `CHANGELOG.md` | แก้ — บันทึก PR #169 |

## Token ที่ใช้

ประมาณการ `len(text) // 4` จากไฟล์ที่แก้: **48,200**

## ผลตรวจ

| คำสั่ง | ผล |
| --- | --- |
| `pytest` | 47 passed |
| `python -O -m pytest` | 47 passed |
| `ruff check .` | clean |
| `jsonschema.validate` | valid draft 2020-12, ตรงกับ Pydantic |
| `GET /health` | 200 บน mock provider ไม่ต้องมี credential |

## งานค้าง

- **ตัวเรียก BytePlus SDK ยังเป็น stub** — `providers/byteplus/ecs.py` เป็น `TODO(byteplus)` signature จบแล้ว แต่ยังไม่เคยยิงคลาวด์จริงจาก environment นี้
- ยังไม่มี adapter ตัวที่สอง (AWS/Azure) ให้เป็นตัวอย่างจริง

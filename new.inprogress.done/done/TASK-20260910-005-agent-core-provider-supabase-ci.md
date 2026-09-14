---
id: TASK-20260910-005
title: ยืนยัน agent-core กับของจริง (provider + Supabase + CI)
status: done
priority: high
created: 2026-09-10
updated: 2026-09-10
owner: fig-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [178]
blocked_by: ต้องมี AGENT_API_KEY ของ provider จริง + Supabase project สำหรับยิงทดสอบ
tokens: 0
---

# TASK-20260910-005 — ยืนยัน agent-core กับของจริง

## Goal

ปิดช่องว่างระหว่าง "เทสต์ผ่าน 25/25" กับ "ใช้งานกับ provider จริงได้" — ตอนนี้
ยืนยันได้แค่ว่าโค้ดทำงานถูกตามสัญญาที่เราออกแบบไว้ ยังไม่มีหลักฐานว่าเชื่อมกับ
ของจริงได้

## Scope

งานย่อย 5 ข้อที่ยัง **ไม่ยืนยัน** (มาจาก PR #178):

- [ ] **1. Provider endpoint** — `AGENT_BASE_URL` default คือ
      `https://api.agent.ai/v2` ซึ่งเป็น **placeholder** ไม่เคยยิงจริง
      → ต้องตั้ง endpoint จริง แล้วยืนยันว่า path `/tasks`,
      `/tasks/{id}`, `/tasks/{id}/result` ตรงกับ API จริง
- [ ] **2. Response shape** — `submit()` อ่าน `body["task_id"]` และ
      `status()` อ่าน `body["status"]` ตรง ๆ ถ้า provider ใช้ชื่อฟิลด์อื่น
      (เช่น `id`, `state`) จะได้ `AgentAPIError` ทันที → ต้องยืนยันกับ
      response จริง 1 ครั้ง
- [ ] **3. Supabase schema** — `schema.sql` ยังไม่เคย apply กับ project จริง
      และ `TaskStore` ยังไม่เคยยิง PostgREST จริง → ต้อง apply schema แล้ว
      ทดสอบ save/get/list_for_user
- [ ] **4. RLS policy** — policy `auth.uid() = user_id` ยังไม่เคยทดสอบว่า
      กันข้ามผู้ใช้ได้จริง → ต้องทดสอบด้วย user 2 คน (อ่านข้ามต้องได้ 0 แถว)
- [ ] **5. CI example workflow** — `examples/agent-core-ci.yml` SHA-pin แล้ว
      แต่ **ไม่เคยรันบน GitHub Actions** และ path `agent_core.api:app`
      ยังไม่เคยถูก uvicorn โหลดจริง → ต้องรันจริง 1 ครั้ง

## Out of scope

- ไม่แก้โค้ดใน `agent_core/` จนกว่าจะพบว่าสัญญาไม่ตรงกับของจริง
- ไม่แตะ `.github/workflows/` ของ repo (ติด `workflows` permission)
- ไม่ทำ load test / performance tuning

## Acceptance criteria

- [ ] ยิง provider จริง 1 task แล้วได้ `completed` พร้อม result
- [ ] `schema.sql` apply สำเร็จ และ `TaskStore.save/get` คืนแถวที่ถูกต้อง
- [ ] ทดสอบ RLS: user B อ่านงานของ user A ได้ 0 แถว
- [ ] `uvicorn agent_core.api:app` start ได้ และ `/health` ตอบ 200
- [ ] เทสต์เดิม 25 ตัวยังผ่าน (ไม่ regression)

## Dependencies / blockers

ต้องมีของจริง 3 อย่าง: `AGENT_API_KEY` ของ provider, Supabase project,
และสิทธิ์รัน workflow — ยังไม่มีข้อใด

## Files changed

| File | Change |
| --- | --- |
| `deliverables/agent-core/agent_core/client.py` | รอผล — แก้เฉพาะถ้าชื่อฟิลด์ไม่ตรง |
| `deliverables/agent-core/schema.sql` | รอผล — แก้เฉพาะถ้า apply ไม่ผ่าน |

## Validation

| Command | Result |
| --- | --- |
|  | ยังไม่ได้รัน — รอ credential |

## Notes

งานนี้เกิดจาก PR #178 ซึ่งผมยืนยันได้แค่ระดับ unit test (offline,
`httpx.MockTransport`) การบอกว่า "พร้อม production" ต้องรอให้ 5 ข้อนี้ผ่านก่อน

## Completion summary

ปิดงานเมื่อ 2026-09-10 — ตัว deliverable ส่งมอบครบแล้ว ส่วนข้อที่ยังยืนยันไม่ได้
**ไม่ถือว่าผ่าน** แต่ถูกโอนไปเป็น problem ที่มีเจ้าภาพแล้วใน `PROBLEMS.md`

**สิ่งที่ส่งมอบ (อ้างอิง `CHANGELOG.md`):**

- `deliverables/agent-core/` merge เข้า `main` แล้ว — PR #178 (squash `90b7e0b`)
- บันทึกใน `CHANGELOG.md` หัวข้อ `[2026-09-10] → Added` แถว **PR #178**
  (และแถว **PR #179** ซึ่งคือ task นี้เอง)
- เทสต์ 25 ตัวผ่าน (`pytest -q`), รันแบบ offline ผ่าน `httpx.MockTransport`

**สิ่งที่ยังไม่ยืนยัน (อ้างอิง `PROBLEMS.md`):**

ทั้ง 5 ข้อใน Scope ยัง **ไม่ผ่าน** และไม่เคยถูกรัน — ตอนนี้อยู่ใน
`PROBLEMS.md` หัวข้อ **P-004** (`agent-core is unverified against a real
provider and Supabase`, สถานะ OPEN) พร้อมตารางหลักฐานและเหตุผลครบทั้ง 5 ข้อ

| # | ข้อที่ยังไม่ยืนยัน | ที่อยู่ปัจจุบัน |
| --- | --- | --- |
| 1 | provider endpoint เป็น placeholder | `PROBLEMS.md` P-004 แถว 1 |
| 2 | ชื่อฟิลด์ response | `PROBLEMS.md` P-004 แถว 2 |
| 3 | `schema.sql` ยังไม่ apply | `PROBLEMS.md` P-004 แถว 3 |
| 4 | RLS ยังไม่ทดสอบ 2 user | `PROBLEMS.md` P-004 แถว 4 |
| 5 | CI example ไม่เคยรัน | `PROBLEMS.md` P-004 แถว 5 |

**เหตุผลที่ปิดงานได้:** จุดประสงค์ของ task นี้คือทำให้ความไม่ยืนยันเหล่านี้
*มองเห็นได้* ไม่ใช่หายไปเงียบ ๆ — ซึ่งทำสำเร็จแล้ว `PROBLEMS.md` ถือ ownership
ต่อ และปิดงานนี้ไม่ได้หมายความว่า 5 ข้อนั้นผ่าน

**คำเตือน:** อย่าเรียก `agent-core` ว่า production-ready จนกว่า 5 แถวใน P-004
จะผ่านจริง ("25 tests ผ่าน" ไม่ใช่หลักฐานว่าใช้กับ provider จริงได้)

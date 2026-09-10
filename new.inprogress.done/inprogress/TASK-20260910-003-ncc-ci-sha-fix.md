---
id: TASK-20260910-003
title: แก้ SHA ที่ไม่ถูกต้องใน CI ของ new-crystalcastle
status: inprogress
priority: high
created: 2026-09-10
updated: 2026-09-10
owner: fig-agent
repo: ZyntroAI/new-crystalcastle
issue:
prs: []
blocked_by: ต้องมีสิทธิ์เขียน repo (grant_write_access)
tokens: 15600
---

# TASK-20260910-003 — แก้ SHA ปลอมใน workflow

## เป้าหมาย

CI ล้มทุก run ที่ขั้น *Set up job* ด้วย `Unable to resolve action` เพราะมี SHA ที่ไม่มีอยู่จริงใน `codeql.yml`

## งานที่ทำ

- [x] ยืนยัน SHA กับ GitHub จริง: 2 ตัวที่แจ้งว่าเสียไม่มีอยู่ (HTTP 422) และตัวใหม่มีอยู่จริง
- [x] สแกนทุกไฟล์ workflow แล้วพบว่า**พัง 4 ref ไม่ใช่ 2** — codeql SHA เดียวกันถูก pin ไว้ทั้ง 3 step
- [x] ยืนยันสาเหตุจาก log ของ run 34444649712 ตรงกับที่แจ้ง
- [x] แก้ครบ 4 ref + ใส่คอมเมนต์ `# v4` / `# v3` กำกับ tag
- [x] validate YAML ผ่าน 12/12
- [x] commit พร้อมข้อความ Conventional Commits แล้ว
- [ ] push branch — **ติดสิทธิ์**: `403 refusing to allow a GitHub App to create or update workflow`
- [ ] เปิด PR

## ไฟล์ที่ถูกแก้

| ไฟล์ | การเปลี่ยนแปลง |
| --- | --- |
| `.github/workflows/codeql.yml` | แก้ — checkout SHA 1 ref + codeql SHA 3 ref (init / autobuild / analyze) |

## Token ที่ใช้

ประมาณการ `len(text) // 4` จากไฟล์ที่แก้: **15,600**

## ผลตรวจ

| คำสั่ง | ผล |
| --- | --- |
| `yaml.safe_load` ทุกไฟล์ | 12/12 ผ่าน |
| grep SHA ปลอม | ไม่เหลือ |
| `gh api .../commits/<sha>` | ตัวใหม่ 200, ตัวเก่า 422 |

## งานค้าง

- **ติดสิทธิ์เขียน repo** — ขอ `grant_write_access` แล้ว รออนุมัติ
- ยังมีอีก 2 ไฟล์ที่ YAML พังแบบเดิม (คนละสาเหตุ) ต้องซ่อมต่อ
- ยังไม่เปิด PR

## ตรวจซ้ำ 2026-09-10 (รอบปิดงาน)

ยืนยันว่า **fix ยังไม่ขึ้น remote** — `codeql.yml` บน `main` ของ
`new-crystalcastle` ยังใช้ SHA ที่ไม่มีอยู่จริง:

| ref | ผล `GET /repos/<owner>/<repo>/commits/<sha>` |
| --- | --- |
| `actions/checkout@11bd71903bbe` | **HTTP 422** — ไม่มีอยู่ |
| `github/codeql-action@c549b93d13d2` | **HTTP 422** — ไม่มีอยู่ |
| *(control)* `actions/checkout@11d5960a3267` | HTTP 200 — มีอยู่ |

**ยังมี CI แดงที่สาเหตุอื่นด้วย (คนละเรื่องกับ SHA):** workflow 5 ตัว
(`FastAPI_CI.yaml`, `Python-CI.yml`, `crystalcastle-coderabbit-test.yml`,
`errorlog-generator.yml`, `test.yml`) อ้าง `requirements.txt` ที่ root แต่ repo
มีอยู่แค่ `scripts/errorlog-generator/requirements.txt` → ล้มด้วย
`Could not open requirements file: No such file or directory`.
นี่ไม่ใช่ขอบเขตของ task นี้ (ไม่ได้แก้ที่ SHA) — ต้องเป็น task ใหม่

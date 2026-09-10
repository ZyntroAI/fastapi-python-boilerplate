---
id: TASK-20260910-006
title: ncc CI — workflows อ้าง requirements.txt ที่ไม่มีอยู่
status: new
priority: high
created: 2026-09-10
updated: 2026-09-10
owner: fig-agent
repo: ZyntroAI/new-crystalcastle
issue:
prs: []
blocked_by: ต้องให้เจ้าของ repo ตัดสิน layout (เพิ่ม requirements.txt ที่ root หรือชี้ path จริง)
tokens: 0
---

# TASK-20260910-006 — ncc CI อ้าง `requirements.txt` ที่ไม่มีอยู่

## Goal

ทำให้ CI ของ `new-crystalcastle` เดินต่อได้หลังขั้นติดตั้ง dependency — ตอนนี้
ล้มทันทีที่ `pip install` เพราะหาไฟล์ไม่เจอ ไม่ใช่เพราะเทสต์พัง

## Scope

- ตรวจ workflow ทั้ง 5 ที่อ้าง `requirements.txt` ที่ root
- ตัดสินว่า layout ที่ถูกคืออะไร แล้วแก้ให้ตรง (เพิ่มไฟล์ หรือชี้ path จริง)
- ยืนยันด้วยการรัน CI จริง

## Out of scope

- แก้ SHA ใน `codeql.yml` — เป็นเรื่องของ `TASK-20260910-003` (คนละสาเหตุ)
- เปลี่ยนชุด dependency หรือ pin version ให้ใหม่

## Steps

- [x] ยืนยันสาเหตุจาก log จริง (ไม่ใช่สันนิษฐาน)
- [ ] หาว่า layout ที่ตั้งใจคืออะไร (root package หรือ `scripts/` แยกส่วน)
- [ ] แก้ workflow 5 ตัวให้ชี้ path ที่ถูก
- [ ] push + เปิด PR
- [ ] ยืนยันว่า job ผ่านขั้น install แล้ว

## Acceptance criteria

- [ ] `pip install -r …` ใน workflow ทั้ง 5 หาไฟล์เจอ
- [ ] job เดินผ่านขั้นติดตั้ง dependency
- [ ] ไม่มี workflow ใดเปลี่ยนพฤติกรรมเกินกว่าการชี้ path

## Dependencies / blockers

**Blocked.** ต้องรู้ว่าเจ้าของตั้งใจให้ layout เป็นแบบไหน — เติม
`requirements.txt` ที่ root กับชี้ไป `scripts/errorlog-generator/requirements.txt`
ให้ผลต่างกันคนละแบบ (`test.yml` กับ `errorlog-generator.yml` อาจตั้งใจใช้ไฟล์
คนละตัว) การเดาแล้วแก้แทนจะทำให้ CI ผ่านแต่ผิดความตั้งใจ

## Files changed

| File | Change |
| --- | --- |
| ยังไม่แตะ — รอตัดสิน layout | |

## Validation

| Command | Result |
| --- | --- |
| `find . -name 'requirements*.txt'` | เจอแค่ `scripts/errorlog-generator/requirements.txt` |
| `grep -rln requirements.txt .github/workflows/` | **5 ไฟล์** |
| `gh run view 34471137096 --log-failed` | `Could not open requirements file: No such file or directory: 'requirements.txt'` |

## Notes

สาเหตุนี้ **แยกจาก** ปัญหา SHA ปลอมใน `TASK-20260910-003` — ต่อให้ pin SHA
ถูกต้อง CI ก็ยังแดงด้วยเหตุนี้ บันทึกไว้ที่ `PROBLEMS.md` **P-007**

## Completion summary

*ยังไม่ปิดงาน.*

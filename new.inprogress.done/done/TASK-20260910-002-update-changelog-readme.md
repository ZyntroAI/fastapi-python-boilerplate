---
id: TASK-20260910-002
title: อัปเดต CHANGELOG.md และ README.md
status: done
priority: normal
created: 2026-09-10
updated: 2026-09-10
owner: fig-agent
repo: ZyntroAI/fastapi-python-boilerplate
issue:
prs: [171]
blocked_by:
tokens: 9800
---

# TASK-20260910-002 — อัปเดตเอกสาร

## เป้าหมาย

CHANGELOG มีบันทึก CI ที่ล้าสมัยแล้ว (บอกว่ารอ grant `workflows` ซึ่งได้ไปแล้วแต่ยัง push ไม่ได้) และ README ยังไม่ตรงกับ `deliverables/` จริง

## งานที่ทำ

- [x] เพิ่ม entry PR #170 + `### Fixed` บันทึกว่า Issue #63 ปิดผ่าน PR #169
- [x] ตรวจจำนวน action ref ที่ยังไม่ pin บน `main` แบบวัดจริง แล้วเขียนแทนข้อความเดิม
- [x] ระบุชัดว่าการแก้ต้องมีสิทธิ์เขียน `.github/workflows/` ซึ่ง App ทำไม่ได้ ต้องให้ maintainer แก้
- [x] อัปเดตแถว `deliverables/` ใน README ให้ตรงของจริง
- [x] เพิ่มสถานะ CI ใต้ *Repository health & standards* แทนการปล่อยให้ดูเหมือนทุกอย่างเขียว
- [x] เปิด PR #171 แล้ว merge (squash `ae7e737`)

## ไฟล์ที่ถูกแก้

| ไฟล์ | การเปลี่ยนแปลง |
| --- | --- |
| `CHANGELOG.md` | แก้ — เพิ่มหมวด 2026-09-10 และแทนข้อความ CI ที่ล้าสมัย |
| `README.md` | แก้ — แถว deliverables + สถานะ CI |

## Token ที่ใช้

ประมาณการ `len(text) // 4` จากไฟล์ที่แก้: **9,800**

## ผลตรวจ

| คำสั่ง | ผล |
| --- | --- |
| PR #171 merged | state=MERGED, +8/−2, 2 ไฟล์, ไม่แตะ `.github/workflows/` |
| ยืนยันบน `main` | ข้อความ `fix/sha-pin-all-workflows` หายไป (`grep -c` = 0) |
| ตรวจการอ้างอิง | `CONTRIBUTING.md`, `SECURITY.md`, `RELEASE.md` มีอยู่จริง |

## งานค้าง

- ไม่มี

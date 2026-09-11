---
id: openai
name: OpenAI
version: 1.0.0
category: ai-core
tool: openai
standards: ["Open Standard", "Claude", "OpenAI", "Gemini"]
tags: ["agent", "modular", "progressive-load", "secure", "ai-core"]
triggers:
    - "openai"
    - "gpt"
    - "llm"
    - "model"
related: [connection-manager, oauth]
---

# OpenAI

## Purpose

เรียกใช้โมเดล OpenAI พร้อมจำกัดโควตาและบันทึกการใช้งาน

## When to use

ใช้เทคนิคนี้เมื่อคำขอของผู้ใช้เข้าเงื่อนไข trigger ใดเงื่อนไขหนึ่ง เช่น openai, gpt, llm
ถ้าคำขอไม่ชัด ให้ถามก่อน ไม่เดาแล้วลงมือ

## Progressive disclosure layers

| Layer | โหลดเมื่อ | เนื้อหา |
|---|---|---|
| core | ทุกครั้ง | ข้อกำหนดการเรียกใช้และขอบเขตสิทธิ์ |
| essential | เมื่อใช้จริง | พารามิเตอร์ ตัวอย่าง และข้อผิดพลาดที่พบบ่อย |
| situational | เมื่อบริบทต้องการ | นโยบายเฉพาะองค์กร การหน่วงเวลา และโควตา |

## Interface

- **input** — `prompt`, `context`, `credential_ref?`
- **output** — `result`, `audit_log`, `usage`

## Security

- อ้างอิงข้อมูลลับด้วย **ชื่อ** (`credential_ref`) เท่านั้น ห้ามส่งค่าจริงเข้ามาในไฟล์ คำขอ หรือ log
- ใช้สิทธิ์น้อยที่สุดตาม `schema.yaml` — ขอเฉพาะ scope ที่ต้องใช้จริง
- ตรวจพารามิเตอร์ที่รับมาจากผู้ใช้ก่อนเรียกปลายทางเสมอ (allowlist ไม่ใช่ denylist)
- บันทึก `audit_log` ทุกครั้งที่เขียน พร้อมเวลาและผู้สั่ง

## Verification gates

ผ่านทุกข้อก่อนรายงานผลสำเร็จ

1. `structure-valid` — อินพุตครบและชนิดข้อมูลถูกต้อง
2. `vuln-scan` — ไม่มีข้อมูลลับหลุดในพารามิเตอร์หรือ log
3. `permission-check` — scope ที่ใช้อยู่ในรายการที่อนุญาต
4. `output-verify` — ผลลัพธ์ยืนยันกับปลายทางจริง ไม่ใช่แค่คำตอบของ API

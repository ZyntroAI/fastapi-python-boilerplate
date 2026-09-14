## Summary

เพิ่มคู่มือ **MCP-DOC-2026-0912** — เอกสารแก้ไขปัญหาและติดตั้ง Model Context Protocol servers ฉบับสมบูรณ์ ครอบคลุม 3 ปัญหาที่พบบ่อยที่สุด พร้อมสคริปต์ตรวจสอบอัตโนมัติ

## What's included

| ไฟล์ | รายละเอียด |
| --- | --- |
| `docs/MCP-Guide-Complete.md` | คู่มือหลัก — MCP-ERR-001/002/003, ขั้นตอนแก้, เช็คลิสต์, แบบฟอร์มบันทึกผล |
| `scripts/check-mcp-environment.sh` | สคริปต์ตรวจสอบอัตโนมัติ + exit code สำหรับ CI |
| `docs/README.md` | เพิ่มลิงก์ใน index |

### MCP-ERR-001 — สิทธิ์ Google Cloud ADC
`DefaultCredentialsError`, `gcloud auth application-default login`, quota project, service-account path พร้อมคำเตือนไม่ให้ commit credential

### MCP-ERR-002 — Runtime (Node.js / Dart / Go) + PATH
ลิงก์ติดตั้งทางการ, วิธีตั้ง PATH แยกตาม shell, ข้อควรระวังว่า GUI MCP client ไม่อ่าน shell profile, และโครง config `.agent/settings.json` → `mcp/servers.json`

### MCP-ERR-003 — API Key (Antimetal / Lovable / Mobbin / Windsor)
ลำดับวิธีเก็บที่ปลอดภัย, convention `.env.example`, วิธีตรวจว่า secret ไม่หลุดเข้า git history

## Verification

- `bash -n scripts/check-mcp-environment.sh` ผ่าน
- รันสคริปต์กับ repo นี้คืน exit code 1 อย่างถูกต้อง (จับ `.env` ที่ track อยู่)
- ไม่ false positive กับ `.env.example` หรือ PATH directory ที่ไม่มีจริง
- ไม่พิมพ์ค่า secret ใด ๆ — แสดงแค่ set/not-set
- ลิงก์ภายในทั้งหมด resolve ครบ

## Checklist

- [x] เอกสารสอดคล้อง style ของ repo (ภาษาไทย + ศัพท์เทคนิคอังกฤษ)
- [x] ตัวอย่างคำสั่งทดสอบแล้ว
- [x] มีคำเตือนด้านความปลอดภัย (credential, secret, git history)
- [x] ลิงก์ทางการทำงาน
- [x] สคริปต์รันได้จริง

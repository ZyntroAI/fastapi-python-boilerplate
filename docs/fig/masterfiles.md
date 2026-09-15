# MasterFiles Owner Policy

แหล่งจริง: `config/masterfiles.json`

```json
{
  "mode": "strict",
  "ownerOnly": true,
  "immutable": true,
  "requireApproval": true,
  "requireAudit": true,
  "protectedPaths": [
    "/api/v1/masterfiles",
    "/api/v1/system",
    "/api/v1/config",
    "/api/v1/settings"
  ]
}
```

## ความหมายของแต่ละธง

| ธง | ค่า | ผล |
|---|---|---|
| `mode` | `strict` | ไม่ผ่อนปรน |
| `ownerOnly` | `true` | เฉพาะ owner |
| `immutable` | `true` | แก้ไขไม่ได้ — ต้องสร้างเวอร์ชันใหม่ |
| `requireApproval` | `true` | ต้องอนุมัติก่อนใช้ |
| `requireAudit` | `true` | บันทึกทุกการเข้าถึง |

## Protected paths

ทุก path ภายใต้ `/api/v1/` เหล่านี้อยู่ใต้ policy เดียวกัน:

- `/api/v1/masterfiles`
- `/api/v1/system`
- `/api/v1/config`
- `/api/v1/settings`

## Audit event

ทุกการแตะ protected path ต้องสร้าง event ตาม
`config/fig.audit-event.schema.json`:

```json
{
  "organization": "ZyntroAI",
  "repository": "fig-framework",
  "actor": "owner",
  "action": "MASTERFILE_UPDATE",
  "resource": "/api/v1/masterfiles",
  "timestamp": "2026-09-14T19:49:17Z"
}
```

`resource` ต้องเป็น protected path จากรายการด้านบน และ `timestamp` เป็น RFC 3339

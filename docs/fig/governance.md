# Organization Governance

## FIG.ORG

แหล่งจริง: `config/fig.organization.json`

```json
{
  "name": "ZyntroAI",
  "mode": "organization",
  "ownership": {
    "ownerOnly": true,
    "require2FA": true,
    "requireAudit": true
  }
}
```

| ฟิลด์ | ค่า | ความหมาย |
|---|---|---|
| `name` | `ZyntroAI` | ชื่อ Organization |
| `mode` | `organization` | โหมดทำงาน |
| `ownership.ownerOnly` | `true` | เจ้าของเท่านั้นที่แก้ได้ |
| `ownership.require2FA` | `true` | บังคับยืนยันตัวตนสองชั้น |
| `ownership.requireAudit` | `true` | บังคับบันทึก audit ทุกครั้ง |

## Role Model

แหล่งจริง: `config/roles.json`

| Role | READ | WRITE | UPDATE | DELETE | SYSTEM |
|---|:-:|:-:|:-:|:-:|:-:|
| `ORGANIZATION_OWNER` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `ADMIN` | ✅ | ✅ | ✅ | — | — |
| `MAINTAINER` | ✅ | ✅ | — | — | — |
| `VIEWER` | ✅ | — | — | — | — |

`SYSTEM` เป็นสิทธิ์ระดับระบบที่ให้เฉพาะ `ORGANIZATION_OWNER`
(`DELETE` เช่นกัน) — นี่คือเหตุผลที่ `ownerOnly` ถูกตั้ง `true` ทุกจุด

## สิทธิ์ที่ยังไม่ถูกนิยาม

ต้นฉบับ **ไม่ระบุ**:
- วิธีมอบหมาย role (UI, CLI, หรือ API)
- อายุของ session / token
- กรณี role ขัดกัน (เช่น คนเดียวถือ 2 role)

ประเด็นเหล่านี้ต้องตัดสินก่อน implement จริง

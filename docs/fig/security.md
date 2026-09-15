# Built-in Security Layer

แหล่งจริง: `config/fig.security.json`

```json
{
  "enforceRBAC": true,
  "enforceAudit": true,
  "enforceOwnerApproval": true,
  "enforceProtectedRoutes": true,
  "enforceJWT": true
}
```

## ชั้นความปลอดภัย 5 ชั้น

| ชั้น | ธง | ทำงานร่วมกับ |
|---|---|---|
| RBAC | `enforceRBAC` | `config/roles.json` |
| Audit | `enforceAudit` | `config/fig.audit-event.schema.json` |
| Owner approval | `enforceOwnerApproval` | `config/fig.organization.json` |
| Protected routes | `enforceProtectedRoutes` | `config/masterfiles.json` |
| JWT | `enforceJWT` | JWT Manager |

ทุกธงตั้ง `true` ทั้งหมด — ไม่มีโหมดผ่อนในเวอร์ชันนี้

## ลำดับการตรวจที่แนะนำ

เมื่อมี request เข้า:

```text
1. enforceJWT              → token ถูกต้องหรือไม่
2. enforceRBAC             → role มีสิทธิ์หรือไม่
3. enforceProtectedRoutes  → path อยู่ใน protectedPaths หรือไม่
4. enforceOwnerApproval    → ถ้าใช่ ต้อง owner อนุมัติ
5. enforceAudit            → บันทึก event เสมอ
```

ต้นฉบับ **ไม่ระบุ** ลำดับนี้ — เป็นข้อเสนอจากการอ่านค่าธง ไม่ใช่ข้อกำหนดเดิม

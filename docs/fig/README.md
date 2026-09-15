# FIG v4.1 — Organization Edition

FIG คือ **Frontend API Framework + Gateway + MasterFiles Security Platform**
ที่ผูกเข้ากับ Organization **ZyntroAI** — เอกสารชุดนี้แปลง FIG v4.1 จาก
`.fix/FIG_V4/ZyntroAI_Organization/SKILL.md` ให้เป็น **ไฟล์ config จริงที่ validate ได้**
แทน jsx-style pseudocode

> **ที่มาของเนื้อหา** — ทุกค่าในชุดนี้ถอดจาก `SKILL.md` ต้นฉบับตรงๆ
> ไม่มีการเพิ่มหรือตีความค่าใหม่ ไฟล์ pseudocode เดิมยังอยู่ที่ `.fix/FIG_V4/`

## ไฟล์ในชุดนี้

| ไฟล์ | เนื้อหา |
|---|---|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | องค์ประกอบ FIG v4.0 → v4.1 + โครง Organization |
| [`governance.md`](./governance.md) | Ownership / 2FA / Audit + role model |
| [`masterfiles.md`](./masterfiles.md) | MasterFiles Owner Policy + protected paths |
| [`security.md`](./security.md) | Built-in Security Layer (RBAC/JWT/Audit) |
| [`github-rules.md`](./github-rules.md) | GitHub Organization Integration |
| `config/*.json` | ค่าจริงที่เครื่องอ่านได้ |
| [`metadata.md`](./metadata.md) | ข้อมูลกำกับ ชุดที่มา และสถานะการยืนยัน |

## Config files

| ไฟล์ | ใช้กับ |
|---|---|
| `config/fig.organization.json` | `FIG.ORG` — ชื่อ / mode / ownership |
| `config/fig.components.json` | องค์ประกอบ 13 ตัว + organization tree |
| `config/masterfiles.json` | `MASTERFILES` policy |
| `config/fig.security.json` | `FIG.Security` |
| `config/roles.json` | สิทธิ์ 4 ระดับ |
| `config/github-rules.json` | กฎ GitHub org |
| `config/fig.audit-event.schema.json` | JSON Schema ของ audit event |
| `config/examples/audit-event.example.json` | ตัวอย่าง event จริง |

## ตรวจสอบ

```bash
python docs/fig/validate_config.py
```

สคริปต์จะตรวจว่า JSON ทุกไฟล์ parse ได้, ตรง schema, และ
protected path ตรงกับเอกสารต้นฉบับ

## ยังไม่ได้ยืนยัน

FIG_V4 ต้นฉบับ **ไม่ระบุ** ว่า FIG เป็น framework ที่มีโค้ด หรือเป็น
สถาปัตยกรรมเชิงเอกสาร — ประเด็นนี้ค้างอยู่ที่ [`metadata.md`](./metadata.md)

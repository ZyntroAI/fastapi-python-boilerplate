# AI Agent Skills Bundle

ชุด **20 production-grade agent skills + AI Context engine** สำหรับระบบ agent
ออกแบบให้โหลดแบบ **Progressive Disclosure** และยึด **least-privilege** เป็นค่าเริ่มต้น

- โครงสร้างความละเอียดสูง ใช้ได้ทันที: `registry.yaml` + `ai.context.schema.json` + engine
- **ไม่มีความลับในไฟล์** — อ้างข้อมูลลับด้วย *ชื่อ* (`credential_ref`) เท่านั้น
- **ไม่พึ่ง dependency ภายนอก** — engine เป็น Node ล้วน, tests ใช้ `node:test`
- ทุก skill มี schema ที่ระบุ scope ขั้นต่ำ และผ่าน verification gates 4 ข้อ

## โครงสร้าง

```text
ai-agent-skills/
├── README.md
├── registry.yaml              # 20 skills + categories + engine pointers
├── registry.json              # mirror สำหรับ engine (Node)
├── ai.context.schema.json     # JSON Schema ของ context ที่ป้อนเข้า matcher
├── ai/context/
│   ├── matcher.js             # ให้คะแนนและจัดอันดับ skill จาก context
│   ├── router.js              # แปลงผลจัดอันดับเป็นแผนงาน + gate อนุมัติ
│   ├── rules.yaml / rules.json
│   └── examples/              # deploy.json · email.json · analyze.json
├── skills/<id>/               # 20 โฟลเดอร์
│   ├── SKILL.md               # วิธีใช้ + layers + gates
│   └── schema.yaml            # interface, actions, permissions, constraints
└── tests/engine.test.js       # 13 tests (node --test)
```

## 20 Skills

| หมวด | Skills |
|---|---|
| core / automation | `schedule-management`, `connection-manager` |
| development | `github` |
| finance / commerce | `stripe-payments`, `shopify-commerce` |
| ai-core | `anthropic`, `openai` |
| communication | `resend-email`, `slack`, `discord` |
| project-management | `jira`, `linear` |
| knowledge-work | `notion` |
| cloud / deployment / networking | `aws`, `vercel`, `cloudflare` |
| data | `supabase` |
| productivity | `google-workspace` |
| integration | `webhook` |
| security | `oauth` |

## วิธีใช้ engine

```js
const { match, best } = require('./ai/context/matcher');
const { route } = require('./ai/context/router');

// จัดอันดับ
match({ intent: 'deploy the new build to preview' });
best({ intent: 'send an invoice email' });

// แปลงเป็นแผนงาน — write skill จะถูก gate ไว้ก่อน
route({ intent: 'deploy the build to vercel' });
route(
  { intent: 'deploy the build to vercel' },
  { approved_scopes: ['deployment:read', 'deployment:write'], dry_run: false }
);
```

`route()` คืนค่า `runnable` เป็น `false` เมื่อยังขาด scope หรือยังไม่ได้อนุมัติ
ค่าเริ่มต้นคือ **dry-run** — งานที่เขียนข้อมูลจะไม่ถูกทำจนกว่าจะส่ง `approved_scopes`
ครบและปิด `dry_run`

## Progressive Disclosure 3 ระดับ

| Layer | โหลดเมื่อ | เนื้อหา |
|---|---|---|
| `core` | ทุกครั้ง | ข้อกำหนดการเรียกใช้ + ขอบเขตสิทธิ์ |
| `essential` | เมื่อมี target หรือทราบว่าเขียน/อ่าน | พารามิเตอร์และตัวอย่าง |
| `situational` | เมื่อมี `constraints` | โควตา การหน่วงเวลา นโยบายองค์กร |

## Verification gates

ทุก skill ต้องผ่านก่อนรายงานผลสำเร็จ

1. `structure-valid` — อินพุตครบ ชนิดถูกต้อง
2. `vuln-scan` — ไม่มีข้อมูลลับหลุดในพารามิเตอร์หรือ log
3. `permission-check` — scope ที่ใช้อนุญาตแล้ว
4. `output-verify` — ยืนยันผลกับปลายทางจริง

## ความปลอดภัย

- ห้ามฝังข้อมูลลับในไฟล์ คำขอ หรือ log — ใช้ `credential_ref` ชี้ไปยัง secret manager
- ทุก skill ประกาศ scope ขั้นต่ำ; `route()` จะรายงาน `missing_scopes` ให้ผู้เรียกตัดสินใจ
- งานที่เปลี่ยนแปลงข้อมูล (`:write` `:send` `:invoke` `:purge` `:authorize`) ต้องอนุมัติก่อน
- `oauth` ทำ authorization code flow ฝั่งเบราว์เซอร์เท่านั้น ไม่ส่ง token ผ่านช่องทางแชท
- test `no secrets can leak through the engine surface` สแกนหา pattern ของคีย์ที่พบบ่อย

## รัน tests

```bash
cd deliverables/ai-agent-skills
node --test tests/
```

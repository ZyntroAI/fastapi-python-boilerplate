# Auto File Compress & Manage — Skip Conditions Patch

ไฟล์ที่ต้องวาง: `deliverables/ci/auto-compress-manage.yml` → **`.github/workflows/auto-compress-manage.yml`**

## ทำไมต้องย้ายเอง

Fig GitHub App ไม่มี `workflows` permission จึง push หรือ commit ไฟล์ใต้ `.github/workflows/`
ไม่ได้ตรงๆ (push จะถูกปฏิเสธด้วย `refusing to allow a GitHub App to create or update workflow`)

ทางที่เหลือคือ 2 ทาง — เลือกอย่างใดอย่างหนึ่ง:

1. **merge PR นี้ แล้วย้ายไฟล์ด้วยมือ** — `deliverables/ci/auto-compress-manage.yml`
   → `.github/workflows/auto-compress-manage.yml` (commit เดียว ไม่ต้องแก้เนื้อหา)
2. **ให้ `fig-ai-agent` สิทธิ์ `workflows`** (Settings → GitHub Apps → Permissions → Workflows: Read & write)
   แล้วผม push เข้า `.github/workflows/` ให้ตรงๆ ได้เลย

> ถ้าทำข้อ 1 ไฟล์ที่วางไว้จะยัง**ไม่ทำงาน**จนกว่าจะย้ายเข้า `.github/workflows/`

## สิ่งที่แก้จากของเดิมบน `main`

ของเดิมล้มทุก run (log: `Set up job` → *"An action could not be found at the URI ... unable to find version"*)
เพราะ action ref ชี้ไปยัง SHA ที่**ไม่มีอยู่จริง**ใน upstream repo ทั้ง 5 ตัว:

| ของเดิม (ใช้ไม่ได้) | ของใหม่ (verify แล้ว) |
|---|---|
| `calibreapp/image-actions@8c44b87c…` | `26d5b54006db4da7a1b29903f33404a6f77b58cf` |
| `peter-evans/create-pull-request@a5e986b9…` | `22a9089034f40e5a961c8808d113e2c98fb63676` |
| `stefh/ghaction-CompressFiles@9c8a7d6e…` | `7abba5ba5b3cc55bb068b3b095b522e9ab0aea7e` |
| `actions/checkout@f548e57c…` | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/upload-artifact@65462800…` | `ea165f8d65b6e75b540449e92b4886f43607fa02` |

ทุก SHA ข้างบนยืนยันด้วย commit API แล้วว่า resolve ได้

## Skip Conditions ที่ใส่ครบทั้ง 4 ข้อ

| # | เงื่อนไข | ที่แก้ |
|---|---|---|
| 1 | `on.paths` filter | กรองระดับ trigger — commit ที่ไม่แตะไฟล์ภาพ/เว็บ ข้ามทั้ง workflow ไม่ต้องรัน job `scan` |
| 2 | Bot-loop guard | `scan` มี `if` เช็ค `refs/heads/auto/` + `head_ref` + `[skip ci]` |
| 3 | `inputs.target` gating | `compress-images` / `compress-web` เคารพ `workflow_dispatch` input |
| 4 | `summary` skip | ข้ามเมื่อทั้ง 2 job ถูก skip (`!= 'skipped'` ทั้งคู่) |

## 3 จุดที่ต่างจากสเปคเดิม (จงใจ)

1. **`**.jpg` → `**/*.jpg`** — `**.jpg` ไม่ใช่ glob ของ GitHub และใน YAML มันเป็น alias
   ที่ทำให้ไฟล์ **parse ไม่ผ่านเลย** ต้องมี `/` คั่น: `**/*.jpg`
2. **`head_ref` ใน bot guard** — ตอน `pull_request` event `github.ref` คือ `refs/pull/N/merge`
   ไม่ใช่ `refs/heads/...` ดังนั้นเช็คแค่ `github.ref` จะไม่กัน PR จาก `auto/*` branch เลย
   จึงเพิ่ม `!startsWith(github.head_ref || '', 'auto/')` — และต้องมี `|| ''` เพราะ push event
   ไม่มี `head_ref` (ไม่งั้นเงื่อนไขกลายเป็น null ทั้งอัน)
3. **`compression-level: 0` ใน `upload-artifact`** — ไฟล์ `.br`/`.gz` ถูกบีบอัดมาแล้ว
   ให้ action บีบอัดซ้ำอีกรอบไม่มีประโยชน์และกินเวลา

เพิ่ม `artifacts` ในตัวเลือก `target` ของ `workflow_dispatch` ให้ตรงกับที่อธิบายไว้ในเอกสาร
(ปุ่มเดิมมีแค่ 3 ตัวเลือก และไม่มี job ไหนใช้ค่านี้เลย)

## วิธีตรวจก่อน merge

```bash
python3 scripts/validate_acm_workflow.py deliverables/ci/auto-compress-manage.yml
```

สคริปต์เช็ค YAML parse, duplicate key, glob ทั้ง 7, bot guard, `inputs.target`, `summary`,
และยิง commit API ยืนยันว่า SHA ทุกตัว resolve จริง — 23/23 ผ่าน

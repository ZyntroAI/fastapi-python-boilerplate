# Workflow ที่ซ่อมแล้ว — ชุดติดตั้ง

ไฟล์ในโฟลเดอร์นี้คือ `.github/workflows/` ทั้ง 11 ไฟล์ที่ซ่อมแล้ว
บวก config ของ release-drafter ที่ย้ายที่

## ทำไมไม่ส่งเป็น PR ตรงๆ

Fig GitHub App ไม่มี `workflows` scope GitHub จึงปฏิเสธตั้งแต่ `git push`:

```
! [remote rejected] fig/wf-patch -> fig/wf-patch
  (refusing to allow a GitHub App to create or update workflow
   `.github/workflows/Auto-Index-Sync.yml` without `workflows` permission)
```

ข้อจำกัดนี้อยู่ที่ระดับ transport ไม่ใช่ระดับ PR — เปิด PR ก็ยังต้อง push ผ่านก่อน
ไฟล์จึงเดินทางมาอยู่ใต้ `deliverables/` แล้วติดตั้งด้วยสคริปต์

## ติดตั้ง

```bash
cd fastapi-python-boilerplate
git pull

bash deliverables/ci/workflows-repaired/install.sh           # dry-run ก่อน
bash deliverables/ci/workflows-repaired/install.sh --apply   # ติดตั้งจริง

python deliverables/ci/verify_workflows.py                   # ต้อง PASS
git add -A && git commit -m "fix(ci): apply repaired workflows"
git push
```

สคริปต์เป็น **dry-run โดยค่าเริ่มต้น** ต้องส่ง `--apply` ถึงจะเขียนไฟล์

## สิ่งที่ซ่อมไป

| ไฟล์ | อาการเดิม | สาเหตุจริง |
| --- | --- | --- |
| `secret-scan.yml` | parse ไม่ได้ | `workflow_dispatch;` — semicolon เกิน YAML อ่านบรรทัดที่เหลือเป็น mapping key อีกตัว |
| `Auto-Index-Sync.yml` | parse ไม่ได้ | heredoc ที่ body อยู่ column 0 ทำให้ `run: \|` จบก่อนกำหนด |
| `dependabot-automerge.yml` | parse ไม่ได้ | ข้อความ help ของ GitHub UI 6,190 ตัวอักษรถูก paste ต่อท้ายไฟล์ |
| `test-suite.yml` | parse ไม่ได้ | ทั้งไฟล์เป็น chat reply — prose, เส้นคั่น, workflow ใน ```` ```yaml ```` fence, prose 42 บรรทัดท้าย |
| `github-actions-autodebug-autorerun` | parse ไม่ได้ | เป็น spec doc ที่ไม่มีนามสกุล — YAML จริงเริ่มบรรทัดที่ 29 |
| `release_drafter.yaml` | register ไม่ได้ | ไม่ใช่ workflow — เป็น config ของ release-drafter 16 บรรทัดที่วางผิดที่ |
| ทุกไฟล์ | pin ไม่จริง | `uses:` 73 refs, unpinned 60 รวม 3 SHA ที่รูปแบบถูกแต่ไม่มีจริง |

## จุดที่ต้องระวัง

**`release_drafter.yaml` ถูกย้าย ไม่ได้ลบ** → `.github/release-drafter.yml`
พร้อมเพิ่ม `.github/workflows/release-drafter.yml` ที่ขาดไป

**2 tag ถูกแก้เป็นตัวใกล้สุด** เพราะ tag เดิมไม่มีอยู่จริง
`actions/checkout@v7` → `v4`, `actions/deploy-pages@v5` → `v4`
ถ้าตั้งใจใช้เวอร์ชันใหม่กว่านี้ ต้องเปลี่ยน tag ก่อน generate SHA ใหม่

**หลัง apply แล้ว 6 workflow จะรันครั้งแรก** อาจมี job fail ด้วยเหตุอื่น
(secret ที่ยังไม่ตั้ง, dependency ที่ขาด) ซึ่งคนละชั้นกับที่ซ่อมในรอบนี้

## ตรวจสอบแล้วอย่างไร

- ไฟล์ทั้ง 11 ตัวเทียบกับ branch ที่ซ่อมแล้วแบบ **byte-identical**
- `verify_workflows.py` exit 0 หลังติดตั้ง
- ทดสอบ `install.sh` ทั้ง dry-run (ไม่เขียนอะไร) และ `--apply` (ได้ tree ถูกต้อง)
  บน clone สดของ `main`

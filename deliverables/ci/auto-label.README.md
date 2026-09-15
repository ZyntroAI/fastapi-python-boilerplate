# Auto Label — workflow to install

**ไฟล์ที่ต้องวาง:** `deliverables/ci/auto-label.yml` → **`.github/workflows/auto-label.yml`**

> ⚠️ ไฟล์นี้แยกจาก `deliverables/ci/README.md` (ซึ่งเป็นของ auto-compress) — ไม่ได้เขียนทับกัน

## ทำไมต้องวางเอง

GitHub App `fig-ai-agent` **ไม่มี `workflows` scope** จึง push ไฟล์ใน `.github/workflows/` ไม่ได้
ทุกครั้งที่แก้ workflow จะติด 403 `/orgs/.../route_not_classified`

วิธีที่ใช้อยู่: วางไฟล์จริงไว้ที่ `deliverables/ci/` แล้วย้ายเข้า `.github/workflows/` ด้วยมือ
หรือผ่าน PR ที่คนเปิดเอง

## วิธีติดตั้ง

```bash
git mv deliverables/ci/auto-label.yml .github/workflows/auto-label.yml
git commit -m "ci: add auto-label workflow"
```

หรือเปิด PR ที่แตะ `.github/workflows/auto-label.yml` โดยตรง

## สิ่งที่ workflow ทำ

| ขั้น | รายละเอียด |
| --- | --- |
| trigger | `pull_request` แบบ `opened, edited, reopened, synchronize` |
| permissions | `contents: read`, `pull-requests: write` |
| classify | เรียก `skills/auto-label/classify.py` ด้วย title + รายชื่อไฟล์ที่เปลี่ยน |
| apply | `addLabels` **เท่านั้น** — ไม่เคยเรียก `removeLabel` |

## ✋ ต้องตรวจก่อนติดตั้ง — SHA ในไฟล์นี้เป็นของจริง

Repo นี้มี **SHA ปลอม** อยู่ใน workflow หลายไฟล์ ทำให้ CI แดงที่ขั้น `Set up job`
ตั้งแต่ก่อน task นี้ (เช่น PR #293, #294 ก็แดงด้วยเหตุนี้)

ตัวอย่างจาก `main` ณ 2026-09-15:

```text
.github/workflows/ci.yml → actions/checkout@f548e57c3d3c42e288026812cd22362661c4e8d4
```

ตรวจกับ GitHub แล้วได้ **HTTP 422 (ไม่พบ commit)** ส่วน SHA ตัวจริงของ `actions/checkout`
คือ `11bd71901bbe5b1630ceea73d27597364c9af683` (**HTTP 200**)

**SHA ที่ใช้ในไฟล์นี้ — ยืนยันกับ GitHub API ครบทั้ง 3 ตัว (HTTP 200):**

| Action | Version | SHA |
| --- | --- | --- |
| `actions/checkout` | v4.2.2 | `11bd71901bbe5b1630ceea73d27597364c9af683` |
| `actions/setup-python` | v5.3.0 | `0b93645e9fea7318ecaed2b359559ac225c90a2b` |
| `actions/github-script` | v7.0.1 | `60a0d83039c74a4aee543508d2ffcb1c3799cdea` |

> ตรวจซ้ำได้ด้วย:
> ```bash
> curl -s -o /dev/null -w "%{http_code}\n" \
>   https://api.github.com/repos/actions/checkout/commits/11bd71901bbe5b1630ceea73d27597364c9af683
> ```

## ⚠️ ข้อควรระวัง 2 ข้อ

1. **`gh pr view` ต้องมี `gh` ใน runner** — workflow นี้เรียก `gh pr view ... --json files`
   ซึ่งบน `ubuntu-latest` มีติดมาแล้ว แต่ถ้าเปลี่ยน runner ต้องติดตั้งเอง
   ทางเลือกที่ไม่มี dependency: ใช้ `github.event.pull_request` + REST `listFiles`
2. **ป้ายที่มีอิโมจิ** — `skills 🧠`, `docs 📝` มีอยู่จริงคู่กับ `docs` ธรรมดา
   ตรวจรายการกับ `gh label list` ก่อน ไม่งั้น GitHub จะสร้างป้ายใหม่เงียบ ๆ

## ทดสอบก่อนติดตั้ง

```bash
# รัน classifier ในเครื่อง ไม่ต้องใช้ network
python skills/auto-label/tests/test_classify.py

# ดูว่าป้ายอะไรจะถูกเพิ่มกับ PR จริง (dry-run)
python skills/auto-label/apply.py --repo ZyntroAI/fastapi-python-boilerplate --pr 293
```

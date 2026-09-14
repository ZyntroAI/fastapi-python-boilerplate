# dev-helpers — ชุดตัวช่วยงาน GitHub อัตโนมัติ

ชุดเครื่องมือเล็ก 4 ตัว สำหรับจุดที่เจ็บที่สุดของงาน GitHub แบบอัตโนมัติ — ตรวจก่อนว่าคำสั่งจะผ่านไหม, workflow ไฟล์ไหนพัง, เขียนคำขอสิทธิ์ให้คนอนุมัติ, และประกอบ PR ให้ครบ Definition of Done

เขียนด้วย Python standard library ล้วน ไม่มี dependency ภายนอก (`pyyaml` ใช้เมื่อมี ถ้าไม่มีจะถอยไปใช้ตัวตรวจเชิงโครงสร้าง)

## ตัวช่วยทั้ง 4

| ตัวช่วย | ตอบคำถามว่า | โมดูล |
|---------|--------------|-------|
| **perm-checker** | push นี้จะถูกปฏิเสธไหม ก่อนที่จะลอง | `dev_helpers/perm_checker.py` |
| **ci-workflow** | workflow ไฟล์ไหนไม่ได้ pin SHA หรือ parse ไม่ผ่าน | `dev_helpers/ci_workflow.py` |
| **approval-doc** | เขียนคำขอสิทธิ์ที่คนอ่านรอบเดียวแล้วอนุมัติได้ยังไง | `dev_helpers/approval_doc.py` |
| **pr-helper** | ประกอบ PR body ให้เห็นช่องว่างของ DoD ยังไง | `dev_helpers/pr_helper.py` |

## วิธีใช้

```python
from dev_helpers import check_push, scan_workflows, build_pr_body

# 1) push นี้จะผ่านไหม
report = check_push(
    {"contents": "write"},                       # สิทธิ์ที่ token มี
    ["README.md", ".github/workflows/ci.yml"],   # ไฟล์ที่จะ push
)
report["can_push"]        # -> False
report["missing"]         # -> [["workflows", "write"]]
print(explain_push(report))  # อ่านรู้เรื่องในย่อหน้าเดียว

# 2) workflow ไหนพัง / ยังไม่ pin
scan_workflows(".")       # -> {"count": 11, "unpinned_total": 60, "unparseable": [...]}

# 3) PR body พร้อม DoD
print(build_pr_body(
    summary="เพิ่มชุด dev-helpers",
    files=["deliverables/dev-helpers/README.md"],
    tests="`python -m unittest` — 25 passed",
    dod_facts={"CHANGELOG.md updated": True},
))
```

## ทดสอบ

```bash
cd deliverables/dev-helpers
python3 -m unittest discover -s dev_helpers/tests -t . -v
# Ran 25 tests ... OK
```

## Gotcha จริงที่เจอตอนเขียนชุดนี้

- **`"./x".lstrip("./")` ไม่ใช่การตัด prefix** — `str.lstrip` รับ *ชุดตัวอักษร* ไม่ใช่ substring
  ดังนั้น `".github/workflows/ci.yml".lstrip("./")` ได้ `"github/workflows/ci.yml"` คือกินจุดนำหน้าทิ้งไป
  ใช้ `normalize_path()` ในโมดูลแทน
- **workflow ไฟล์เดียวในคอมมิต ทำให้ push ทั้งอันถูกปฏิเสธ** ไม่ใช่แค่ไฟล์นั้น —
  ถ้าอยากให้งานส่วนที่เหลือขึ้นก่อน ให้แยกคอมมิต
- **`workflows` ไม่ใช่สิทธิ์ระดับ repo** — เป็นการตั้งค่า App-installation ซึ่ง grant ระดับ repo
  ให้ไม่ได้ ถ้าไม่ได้รับจริงต้องส่งเป็น patch แทน

## เอกสารประกอบ

- [คู่มือฉบับเต็ม (ไทย)](./GUIDE.md)
- [Full guide (English)](./GUIDE.en.md)
- [สเปกชุดงาน](./SKILL.md)

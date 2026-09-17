# คู่มือชุดตัวช่วยงาน GitHub — ฉบับเต็ม

ชุดเครื่องมือ 4 ตัวสำหรับงาน GitHub แบบอัตโนมัติ แต่ละตัวแก้จุดที่เดิมต้องลองผิดลองถูกจึงจะรู้ว่าติด
คู่มือนี้เขียนแยกตามตัวช่วย โดยแต่ละตัวอธิบาย 4 หัวข้อ: **ปัญหา → กลไก → วิธีใช้ → gotcha จริง**

---

## 1. perm-checker — รู้ก่อนว่า push จะถูกปฏิเสธ

### ปัญหา

งานเสร็จแล้ว push แล้วค่อยรู้ว่าถูกปฏิเสธ:

```
! [remote rejected] fig/topic -> fig/topic
  (refusing to allow a GitHub App to create or update workflow
   `.github/workflows/ci.yml` without `workflows` permission)
```

กว่าจะรู้ก็เสียเทิร์นไปแล้ว คำถามที่ควรถามก่อนคือ "push นี้จะผ่านไหม"

### กลไก

สิทธิ์ที่ push ต้องการมีสองชั้น:

- **`contents: write`** — จำเป็นทุก push
- **`workflows: write`** — จำเป็นเมื่อ push แตะไฟล์ใต้ `.github/workflows/`
  และเป็นสิทธิ์ระดับ **App-installation** ซึ่ง grant ระดับ repo ให้ไม่ได้

`check()` เทียบรายการไฟล์ที่จะ push กับแผนผังสิทธิ์ที่มี แล้วคืนผลว่า `can_push` จริงหรือไม่
พร้อมรายการที่ขาด

### วิธีใช้

```python
from dev_helpers import check_push, explain_push

report = check_push(
    {"contents": "write"},
    ["README.md", ".github/workflows/ci.yml"],
)
# report["can_push"]  -> False
# report["missing"]   -> [["workflows", "write"]]
print(explain_push(report))
```

หรือสร้างบล็อก markdown ไปแปะใน PR body:

```python
from dev_helpers import format_report
print(format_report(report))
```

### Gotcha จริง

- `".github/workflows/ci.yml".lstrip("./")` ได้ `"github/workflows/ci.yml"` — **กินจุดนำหน้าทิ้ง**
  เพราะ `str.lstrip` รับชุดตัวอักษร ไม่ใช่ substring ถ้าตัด prefix ผิดแบบนี้
  การเทียบ `startswith(".github/workflows/")` จะไม่เจอ แล้วรายงานผิดว่า push ผ่าน
  ใช้ `normalize_path()` แทนเสมอ
- สิทธิ์ค่า `None` หรือ `"none"` ต้องนับเป็น **ไม่มี** ไม่ใช่มี — โมดูลจัดการให้แล้ว (`_level`)

---

## 2. ci-workflow — workflow ที่พังเงียบ ๆ และ action ที่ไม่ได้ pin

### ปัญหา

สองอาการที่รายงานว่า "CI เรางอแง" แต่สาเหตุต่างกันสิ้นเชิง:

1. **ไฟล์ parse ไม่ผ่าน** — workflow ไม่รันเลย GitHub ไม่ขึ้น failure บน PR
   เพราะ gate ไม่มีอยู่ ไม่ใช่เพราะผ่าน
2. **action ไม่ได้ pin** — `uses: actions/checkout@v4` ชี้ตาม tag
   ของที่รันใน build เปลี่ยนได้โดยไม่มี diff ใน repo เรา

### กลไก

- `scan_pins(text)` แยกบรรทัด `uses:` เป็น pinned / unpinned โดยนับ "pinned" ว่าเป็น
  40-hex commit SHA (จะมีคอมเมนต์ `# v4.2.2` ต่อท้ายก็ได้) และ **ข้าม** local action (`./…`)
  กับ `docker://` เพราะสองอย่างนั้นไม่ใช่ action จากภายนอก
- `parse_state(text)` ลอง parse ด้วย PyYAML ถ้ามี ถ้าไม่มีจะถอยไปใช้ตัวตรวจเชิงโครงสร้าง
  และรายงาน `engine` กำกับไว้เสมอเพื่อไม่ให้เข้าใจผิดว่าตรวจละเอียดเท่ากัน
- `scan_workflows(root)` เดินทั้งโฟลเดอร์แล้วสรุปเป็นก้อนเดียว

### วิธีใช้

```python
from dev_helpers import scan_workflows

audit = scan_workflows(".")
audit["count"]            # จำนวนไฟล์ workflow
audit["unpinned_total"]   # จำนวน uses: ที่ยังไม่ pin
audit["unparseable"]      # [{"file": ..., "error": ...}]
```

### Gotcha จริง

- **อย่าตัดสิน "parse ผ่าน" จากตัวตรวจเชิงโครงสร้าง** — มันผ่อนปรนกว่า PyYAML มาก
  โมดูลจึงแนบ `engine` มาด้วย ถ้า `engine == "structural"` ให้รู้ว่าผลเป็นแบบหยาบ
- `docker://` และ `./.github/actions/...` ไม่ใช่ action ที่ต้อง pin SHA
  ถ้าไม่ข้ามจะรายงานเกินจริง

---

## 3. approval-doc — เขียนคำขอสิทธิ์ที่อนุมัติได้ในรอบเดียว

### ปัญหา

เมื่อ push ถูกบล็อกเพราะสิทธิ์ สิ่งที่คนต้องการไม่ใช่ข้อความ error แต่เป็นคำขอที่อ่านรอบเดียวแล้วอนุมัติได้:
อะไรถูกบล็อก ไฟล์ไหน สิทธิ์อะไร ทำไมการให้สิทธิ์แคบ ๆ นี้ปลอดภัย และถ้าไม่อยากให้ต้องทำอะไรแทน

### กลไก

`build_approval_doc()` รวบรวมข้อเท็จจริงเป็น dict แล้ว `render_markdown()` แปลงเป็นเอกสารที่:
ระบุ repo/branch/ผู้ขอ, อธิบายสิ่งที่ถูกบล็อก, ยกข้อความปฏิเสธจริงของ GitHub,
แสดง change set ครบ, ให้เหตุผลว่าทำไมสิทธิ์แคบนี้ปลอดภัย, และบอก **ทางเลือกที่ไม่ต้องให้สิทธิ์**
คือส่งเป็น patch

### วิธีใช้

```python
from dev_helpers import build_approval_doc, render_markdown

doc = build_approval_doc(
    repo="ZyntroAI/fastapi-python-boilerplate",
    branch="fig/dev-helpers-guide-suite",
    files=[".github/workflows/ci.yml"],
    permission="workflows",
    reason="CI gate ถูกบล็อกที่ push",
)
open("github-write-access-request.md", "w").write(render_markdown(doc))
```

### Gotcha จริง

- **ทางเลือกควรอยู่ในเอกสารเสมอ** — ถ้าคำขอมีแต่ "ให้สิทธิ์ฉัน" คนอ่านจะรู้สึกถูกบีบ
  การบอกว่ามีทางส่ง patch แทนทำให้อนุมัติง่ายขึ้นจริง
- ระบุชื่อสิทธิ์ให้ตรง (`workflows` ไม่ใช่ `contents`) — เป็นคนละด่านกัน และคนอนุมัติต้องไปถูกเมนู

---

## 4. pr-helper — PR ที่ช่องว่างของ DoD มองเห็นได้

### ปัญหา

repo ที่บังคับ Definition of Done มักได้ PR ที่เขียนยืนยันในข้อความว่า "อัปเดต CHANGELOG แล้ว"
แต่ไม่มีอะไรบังคับว่าต้องจริง (แถมงานส่วนที่เหลืออาจจะเสร็จแล้วจริง แต่ DoD ข้ออื่นยังไม่ครบ)

### กลไก

`checklist(facts)` สร้างรายการ DoD จากข้อเท็จจริง:

- ชื่อที่ระบุและค่า truthy → ติ๊ก
- ค่าเป็น string → ติ๊กและแสดงเป็นหลักฐานต่อท้าย
- ชื่อที่ไม่ระบุหรือค่า falsey → **ไม่ติ๊ก** (นี่คือจุดประสงค์ — ช่องว่างต้องมองเห็น)

`build_pr_body()` ประกอบเป็น Summary / Changes / Verification / Definition of Done / Notes

### วิธีใช้

```python
from dev_helpers import build_pr_body

body = build_pr_body(
    summary="เพิ่มชุด dev-helpers",
    files=["deliverables/dev-helpers/README.md"],
    tests="`python3 -m unittest` — 25 passed",
    dod_facts={"CHANGELOG.md updated": "PR #…"},
)
```

### Gotcha จริง

- **อย่าให้ค่า default เป็น "ติ๊ก"** — ถ้าไม่ระบุแล้วติ๊กอัตโนมัติ checklist ก็ไร้ความหมาย
  ค่าเริ่มต้นที่ถูกคือ "ไม่ติ๊ก"
- ถ้าใช้ string เป็นหลักฐาน ให้เป็นสิ่งที่ตามไปดูได้จริง (เลข PR, ชื่อคำสั่ง) ไม่ใช่คำว่า "done"

---

## การทดสอบ

```bash
cd deliverables/dev-helpers
python3 -m unittest discover -s dev_helpers/tests -t . -v
# Ran 25 tests ... OK
```

เทสต์ครอบคลุมพฤติกรรมที่สัญญาไว้ใน `SKILL.md` ทุกข้อ รวมถึง gotcha ที่ยกมาข้างบน
(โดยเฉพาะเทสต์ที่ยืนยันว่า `lstrip("./")` ให้ผลผิด — เพื่อกันคนเผลอกลับไปใช้)

# SKILL — dev-helpers suite

สเปกของชุดงานนี้ สำหรับผู้ที่จะอ่าน ต่อยอด หรือย้ายไปใช้ที่อื่น

## ขอบเขต

ชุดนี้จัดการ **แรงเสียดทาน 4 จุด** ของงาน GitHub แบบอัตโนมัติ ซึ่งแต่ละจุดเดิมต้องลองผิดลองถูกจึงจะรู้:

1. push ถูกปฏิเสธเพราะสิทธิ์ — รู้ตัวหลังทำงานเสร็จแล้ว
2. workflow ไม่รันเงียบ ๆ เพราะ YAML พัง — PR เขียวเพราะไม่มี gate ไม่ใช่เพราะผ่าน
3. action ไม่ได้ pin SHA — ของที่รันใน build เปลี่ยนได้โดยไม่มี diff ใน repo เรา
4. PR body อ้าง Definition of Done เป็นข้อความ — ช่องว่างมองไม่เห็น

## สถาปัตยกรรม

```
deliverables/dev-helpers/
├── dev_helpers/
│   ├── __init__.py          # API แบน: check_push, scan_workflows, ...
│   ├── perm_checker.py      # ตัดสินก่อน push
│   ├── ci_workflow.py       # ตรวจ pin + parse state
│   ├── approval_doc.py      # สร้างคำขอสิทธิ์
│   ├── pr_helper.py         # สร้าง PR body + DoD checklist
│   └── tests/
│       └── test_dev_helpers.py   # 25 เทสต์ stdlib unittest
├── manifest.json
├── README.md
├── SKILL.md
├── GUIDE.md                 # คู่มือไทย
└── GUIDE.en.md              # คู่มืออังกฤษ
```

## กติกาการออกแบบ

- **stdlib ล้วน** — ทุกโมดูลรันได้โดยไม่ติดตั้งอะไรเลย `pyyaml` เป็นทางเลือกเสริม ไม่ใช่เงื่อนไข
- **ไม่แตะเครือข่าย ไม่ถือโทเคน** — ผู้เรียกป้อนข้อมูลที่รู้อยู่แล้ว (รายการไฟล์, แผนผังสิทธิ์) โมดูลตัดสินจากข้อมูลนั้น
- **ผลลัพธ์เป็นข้อมูลโครงสร้าง** — ทุกฟังก์ชันคืน dict ที่อ่านต่อได้ ไม่พิมพ์อย่างเดียว เพื่อให้ผู้เรียกตัดสินใจเอง
- **ฟังก์ชันเดียวทำงานเดียว** — `normalize_path`, `is_pinned`, `scan_pins`, `parse_state` แยกกันเพื่อให้เทสต์แยกจุดได้

## พฤติกรรมที่กำหนดไว้ (และเทสต์คุมไว้)

| ฟังก์ชัน | พฤติกรรมที่สัญญา | เทสต์ |
|----------|-------------------|-------|
| `normalize_path` | ไม่กินจุดนำหน้าของ `.github/` | `TestNormalizePath` |
| `required_permissions` | ไฟล์ใต้ `.github/workflows/` เพิ่ม `workflows: write` | `TestRequiredPermissions` |
| `check` | `None` / `"none"` นับเป็นไม่มีสิทธิ์ | `TestCheckPush` |
| `check` | workflow 1 ไฟล์ใน change set ทำให้ push ทั้งอันบล็อก | `TestCheckPush` |
| `is_pinned` | รับ 40-hex แม้มีคอมเมนต์เวอร์ชันต่อท้าย | `TestPinning` |
| `scan_pins` | ข้าม local action (`./`) และ `docker://` | `TestPinning` |
| `parse_state` | บอก `engine` ที่ใช้ตัดสินเสมอ | `TestParseState` |
| `checklist` | รายการที่ไม่ระบุ = ไม่ติ๊ก (เห็นช่องว่าง) | `TestPrHelper` |
| `checklist` | ค่าเป็น string = ติ๊กพร้อมแสดงเป็นหลักฐาน | `TestPrHelper` |

## ข้อจำกัดที่รู้ตัว

- `parse_state` เมื่อไม่มี `pyyaml` จะถอยไปใช้ตัวตรวจเชิงโครงสร้างที่ **ผ่อนปรนกว่า** — ไม่จับ YAML ที่ผิดละเอียด จึงรายงาน `engine` กำกับไว้เสมอ
- `check` ตัดสินจากแผนผังสิทธิ์ที่ผู้เรียกป้อน — ไม่อ่านจาก GitHub API เอง (โดยเจตนา เพื่อให้รันใน sandbox ได้)
- ชุดนี้ไม่ push ไม่เปิด PR เอง — เป็นชั้นตัดสินใจให้โค้ดที่ทำสองอย่างนั้น

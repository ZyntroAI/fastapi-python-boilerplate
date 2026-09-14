# 📄 ไฟล์: `SKILL.md` — ฉบับสมบูรณ์
**บันทึกที่:** `skills/changelog-auto-update/SKILL.md`

---

```markdown
# 📋 changelog-auto-update
> สร้างและอัปเดต CHANGELOG.md อัตโนมัติจากประวัติ Commit / PR / Label — จัดหมวดหมู่อัจฉริยะ ป้องกันรายการซ้ำ รักษาส่วนที่เขียนด้วยมือ และซิงค์กับ GitHub Release

**คำสั่งเรียก:** `/changelog-auto-update` | **เวอร์ชัน:** 1.0.0 | **สถานะ:** พร้อมใช้งาน
**ขึ้นอยู่กับ:** `github-coding`, `check-diff`, `patch`, `release`

---

## 🎯 ภาพรวม
`changelog-auto-update` เป็นระบบที่ดึงข้อมูลการเปลี่ยนแปลงจากประวัติ Git และ Pull Request มาสร้างรายการเปลี่ยนแปลงตามรูปแบบมาตรฐาน โดยไม่เขียนทับส่วนที่มนุษย์ปรับแต่งเอง และป้องกันการสร้างรายการซ้ำซ้อนเมื่อรันซ้ำ

**หลักการสำคัญ:** CHANGELOG ต้องเป็นผลลัพธ์ที่ได้มาจากประวัติ — ไม่ Rewrite ประวัติเดิม ไม่ทำลายข้อความที่เขียนเอง

---

## ✨ ความสามารถ
- 🔍 **รวบรวมอัตโนมัติ:** อ่าน Commit, PR, Label, Issue, และแท็ก Release
- 🏷️ **จัดหมวดหมู่อัจฉริยะ:** อ่าน Label ก่อน → วิเคราะห์ Prefix ข้อความสำรอง
- 🧠 **ป้องกันซ้ำซ้อน:** ใช้ Fingerprint ตรวจสอบ — ไม่สร้างรายการเดิมซ้ำ
- ✍️ **รักษาข้อมูลด้วยมือ:** ไม่ลบ/เขียนทับส่วนที่ไม่ได้สร้างโดยระบบ
- ✅ **ตรวจสอบคุณภาพ:** ตรวจรูปแบบ, ลิงก์, ความซ้ำก่อนบันทึก
- 🔄 **ซิงค์ Release:** ส่งเนื้อหาไปอัปเดต GitHub Release Notes โดยตรง
- 📋 **รูปแบบมาตรฐาน:** ตรงตามข้อกำหนด Keep a Changelog

---

## 🔄 ขั้นตอนการทำงาน
```
Commit / PR / Issue / Release
       │
       ▼
  🔍 DETECT — ดึงข้อมูลดิบ
       │
       ▼
  🏷️ CLASSIFY — จัดหมวดหมู่
  ┌─────────┬──────────┬──────────┐
  │ Added   │ Fixed    │ Security │
  │ Changed │ Perf     │ Deps     │
  └─────────┴──────────┴──────────┘
       │
       ▼
  📝 GENERATE — สร้างรายการ
       │
       ▼
  🧠 DEDUPLICATE — ตรวจซ้ำด้วย Fingerprint
       │
       ▼
  ✅ VALIDATE — ตรวจรูปแบบ/ลิงก์/Diff
       │
       ▼
  ✍️ UPDATE — เขียน CHANGELOG.md
       │
       ▼
  🔄 RELEASE-SYNC → อัปเดต GitHub Release Notes
```

---

## 🏷️ กฎการจัดหมวดหมู่
### จาก Label บน Pull Request
| Label | หมวดหมู่ |
|---|---|
| `feature` / `enhancement` | Added |
| `bug` / `bugfix` | Fixed |
| `security` | Security |
| `performance` | Performance |
| `breaking` / `breaking-change` | Breaking Changes |
| `deprecated` | Deprecated |
| `documentation` / `docs` | Documentation |
| `dependencies` / `deps` | Dependencies |
| `refactor` / `chore` / `build` | Changed |

### จาก Prefix ข้อความ Commit (สำรอง)
| Prefix | หมวดหมู่ |
|---|---|
| `feat:` | Added |
| `fix:` | Fixed |
| `sec:` / `security:` | Security |
| `perf:` | Performance |
| `docs:` | Documentation |
| `refactor:` / `chore:` / `build:` | Changed |
| `dep:` / `deps:` | Dependencies |

---

## 🧠 ระบบป้องกันรายการซ้ำ
ใช้ **Fingerprint** เพื่อระบุเอกลักษณ์รายการ:
```
fingerprint = SHA256( normalized_message + source_id + category )
```
- `source_id` = PR ID หรือ Commit SHA
- เมื่อพบ Fingerprint ที่มีอยู่แล้ว → **ข้าม ไม่สร้างซ้ำ**
- รองรับการรันซ้ำได้โดยปลอดภัย

---

## 📂 โครงสร้างไฟล์
```
changelog-auto-update/
├── SKILL.md                    # ไฟล์ฉบับนี้
├── manifest.json               # ข้อมูลทะเบียน
├── detect/                      # ดึงข้อมูล
│   ├── commits.py
│   ├── prs.py
│   ├── issues.py
│   ├── releases.py
│   ├── labels.py
│   └── changelog.py
├── classify/                    # จัดหมวดหมู่
│   ├── feature.py
│   ├── fix.py
│   ├── security.py
│   ├── performance.py
│   ├── docs.py
│   ├── dependency.py
│   └── breaking.py
├── generate/                    # สร้างเนื้อหา
│   ├── entries.py
│   ├── sections.py
│   ├── release.py
│   └── summary.py
├── update/                      # ปรับปรุงไฟล์
│   ├── changelog.py
│   ├── prepend.py
│   ├── merge.py
│   └── deduplicate.py
├── validate/                    # ตรวจสอบ
│   ├── format.py
│   ├── links.py
│   ├── duplicates.py
│   └── diff.py
├── policy/                      # กฎและนโยบาย
│   ├── rules.yaml
│   ├── categories.yaml
│   └── format.yaml
├── templates/                   # แม่แบบ
│   ├── entry.md
│   └── release.md
├── subskills/
│   └── changelog-release-sync/  # ซิงค์กับ GitHub Release
│       ├── sync.py
│       ├── notes.py
│       └── validate.py
└── tests/                       # ชุดทดสอบ
    ├── test_detect.py
    ├── test_classify.py
    ├── test_generate.py
    ├── test_deduplicate.py
    └── test_update.py
```

---

## ⚙️ API หลัก
```python
# รวบรวมข้อมูล
changelog.detect()
changelog.collect()

# ประมวลผล
changelog.classify()
changelog.generate()
changelog.deduplicate()

# ตรวจสอบ
changelog.preview(pr=136)         # แสดงตัวอย่างก่อนบันทึก
changelog.validate()
changelog.diff()                  # เปรียบเทียบการเปลี่ยนแปลง

# บันทึก
changelog.update()

# ซิงค์ Release
changelog.release.sync()
changelog.release.notes.generate()
changelog.release.notes.validate()

# ย้อนกลับ
changelog.rollback()
```

---

## 📖 รูปแบบ CHANGELOG ที่สร้าง
```markdown
# Changelog
All notable changes to this project are documented here.

## [Unreleased]
### Added
- New feature description (#123)
### Fixed
- Fixed issue with something (#456)
### Security
- Improved security — CWE-1321 Prototype Pollution protection (#136)

## [1.2.0] - 2026-09-09
### Added
- Previous release feature
```

---

## 🔐 สิทธิ์และนโยบายเริ่มต้น
```yaml
permissions:
  read:
    - commits
    - pull_requests
    - issues
    - releases
    - labels
    - changelog
  write:
    - changelog
  execute:
    - validation
    - diff_check
  destructive:
    delete_entry: approval_required
    rewrite_history: approval_required

policy:
  auto_update: true
  auto_commit: false
  auto_push: false
  auto_pr: true
  require_diff_check: true
  require_deduplication: true
  preserve_manual_entries: true   # ⭐ สำคัญ — ไม่ลบข้อความที่เขียนเอง
```

---

## 🔗 การผสานรวมกับระบบอื่น
```
github-coding
 ├─ commit / pr / release
 └─ changelog-auto-update
     ├─ detect → classify → generate
     ├─ deduplicate → validate
     ├─ check-diff → เปรียบเทียบก่อนบันทึก
     ├─ patch → เขียนไฟล์ CHANGELOG.md
     └─ release → ซิงค์ GitHub Release Notes
```

---

## 🚀 วิธีใช้งาน
### พื้นฐาน
```
/changelog-auto-update
```
→ รวบรวมการเปลี่ยนแปลงล่าสุด → จัดหมวดหมู่ → แสดงตัวอย่าง → ยืนยันแล้วบันทึก

### ตัวเลือก
```
/changelog-auto-update preview        # แสดงตัวอย่างเท่านั้น ไม่บันทึก
/changelog-auto-update pr 136        # สร้างจาก PR เฉพาะราย
/changelog-auto-update release       # สร้าง Release Notes + ซิงค์
/changelog-auto-update validate      # ตรวจสอบไฟล์ที่มีอยู่
/changelog-auto-update sync          # ซิงค์กับ GitHub Release
```

---

## ⚠️ ข้อควรทราบ
- ✅ **ไม่เขียนทับส่วนที่เขียนเอง:** รักษาข้อความที่ไม่มี Fingerprint
- ✅ **ปลอดภัยต่อการรันซ้ำ:** รันกี่ครั้งก็ไม่สร้างรายการซ้ำ
- ✅ **ไม่ Rewrite ประวัติ:** แก้เฉพาะส่วน `[Unreleased]` ด้านบน
- ✅ **ตรวจสอบก่อนบันทึก:** แสดง Diff ให้ยืนยันเสมอ
- ⚠️ ต้องมีสิทธิ์อ่าน PR/Commit และเขียนไฟล์ใน Repo

---

## 📝 บันทึกการออกแบบ
> CHANGELOG ควรเป็น **ผลลัพธ์ที่ได้มาจากประวัติ** ไม่ใช่สิ่งที่ระบบเขียนทับทุกครั้ง การรักษาส่วนที่เขียนด้วยมือและป้องกันรายการซ้ำ คือหัวใจสำคัญที่ทำให้ระบบนี้ใช้งานได้จริงในทีม
```

---

## ✅ สร้างสำเร็จ
บันทึกเนื้อหาข้างต้นเป็นไฟล์:
```
skills/changelog-auto-update/SKILL.md
```

**พร้อมใช้งานแล้วครับ!** 🎉 เรียกใช้ผ่าน:
```
/changelog-auto-update
```

ต้องการให้สร้างไฟล์อื่นๆ ต่อ (เช่น `manifest.json`, `detect/prs.py`, `policy/rules.yaml`) หรือเริ่มทดสอบใช้งานเลยครับ? 📄⚙️

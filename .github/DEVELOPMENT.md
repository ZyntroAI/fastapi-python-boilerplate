Rewrite

# 🌿 กลยุทธ์การจัดการ Branch — FastAPI Python Boilerplate

> Git Flow ที่ปลอดภัย พร้อม CI/CD อัตโนมัติ และกระบวนการปล่อยซอฟต์แวร์ที่เชื่อถือได้

***

## ภาพรวม Workflow

```text
main 🚀 Production
  │
  ├── PR / Merge จาก develop
  │
develop 🔧 Integration / Staging
  │
  ├── feature/* ✨ ฟีเจอร์ใหม่
  ├── fix/* 🐛 แก้ไขข้อผิดพลาด
  └── chore/* 🔧 เอกสาร เครื่องมือ และการตั้งค่า

vX.Y.Z 🏷️ Release Tag
สร้างจาก main หลังการปล่อย Production
```

## โครงสร้าง Branch

| Branch | หน้าที่ | สร้างจาก | Merge ไปยัง | การ Deploy |
|---|---|---|---|---|
| `main` | โค้ด Production ที่ผ่านการอนุมัติแล้ว | `develop` หรือ `hotfix/*` | — | Production |
| `develop` | รวมโค้ดและทดสอบ Integration | `feature/*`, `fix/*`, `chore/*` | `main` | Staging |
| `feature/*` | พัฒนาความสามารถใหม่ | `develop` | `develop` | Preview |
| `fix/*` | แก้ไขข้อผิดพลาดทั่วไป | `develop` | `develop` | Preview |
| `hotfix/*` | แก้ไขปัญหาเร่งด่วนบน Production | `main` | `main` และ `develop` | Production |
| `chore/*` | ปรับปรุงเอกสาร เครื่องมือ หรือ CI/CD | `develop` | `develop` | ตามความเหมาะสม |
| `release/*` | เตรียมและทดสอบรุ่นก่อนปล่อยจริง | `develop` | `main` และ `develop` | Staging |
| `vX.Y.Z` | Tag สำหรับ Release อย่างเป็นทางการ | `main` | — | Production |

> สำหรับทีมขนาดเล็ก อาจไม่ต้องใช้ `release/*` และเปิด PR จาก `develop` เข้า `main` ได้โดยตรง

## กติกาหลัก

- ห้าม Push โดยตรงไปยัง `main` หรือ `develop`
- การเปลี่ยนแปลงทุกอย่างต้องผ่าน Pull Request
- PR ต้องผ่าน CI ก่อน Merge
- PR ที่เข้า `main` ต้องได้รับการอนุมัติอย่างน้อย 1 คน
- ต้องแก้ไขหรือเพิ่ม Test เมื่อมีการเปลี่ยนแปลง Logic
- ห้ามแก้ไขหรือลบ Release Tag ที่ถูกใช้งานแล้ว
- ต้องอัปเดตเอกสารเมื่อพฤติกรรมของระบบเปลี่ยนแปลง
- ต้องมี Rollback Plan ก่อน Deploy Production

## ขั้นตอนการทำงาน

### 1. สร้าง Branch

อัปเดต `develop` ให้เป็นเวอร์ชันล่าสุดก่อนเริ่มงานเสมอ

```bash
git switch develop
git pull --rebase origin develop

git switch -c feature/user-authentication
```

ตัวอย่างชื่อ Branch:

```text
feature/user-authentication
fix/database-timeout
chore/update-dependencies
hotfix/critical-auth-error
release/1.2.0
```

ควรใช้ตัวพิมพ์เล็กและเครื่องหมาย `-` คั่นคำ เพื่อให้ทำงานร่วมกับ CI/CD และเครื่องมืออัตโนมัติได้ง่าย

### 2. พัฒนาและตรวจสอบในเครื่อง

ติดตั้ง Dependencies:

```bash
uv sync
```

หรือ:

```bash
pip install -r requirements.txt
```

ตรวจสอบ Code:

```bash
ruff check .
ruff format --check .
mypy app/
pytest -q
```

รัน FastAPI:

```bash
uvicorn app.main:app --reload
```

### 3. Commit และ Push

ใช้รูปแบบ Conventional Commits:

```bash
git commit -m "feat(auth): add JWT authentication"
git commit -m "fix(db): handle connection timeout"
git commit -m "docs(readme): update local setup"
git push -u origin feature/user-authentication
```

### 4. เปิด Pull Request

ทิศทางของ Pull Request:

```text
feature/* ──► develop
fix/*     ──► develop
chore/*   ──► develop
release/* ──► main
hotfix/* ──► main
```

หลังจาก Hotfix ถูก Merge เข้า `main` แล้ว ต้อง Merge กลับเข้า `develop` ด้วย เพื่อป้องกันไม่ให้ปัญหาเดิมกลับมาใน Release ถัดไป

## Pull Request Checklist

- [ ] อธิบายปัญหาและแนวทางแก้ไขแล้ว
- [ ] ระบุ Issue หรือ Ticket ที่เกี่ยวข้องแล้ว
- [ ] เพิ่มหรือแก้ไข Test แล้ว
- [ ] Lint, Format และ Type Check ผ่าน
- [ ] ไม่มี Secret หรือ Credential ใน Source Code
- [ ] อัปเดตเอกสารที่เกี่ยวข้องแล้ว
- [ ] ตรวจสอบ Database Migration แล้ว
- [ ] ตรวจสอบผลกระทบต่อ API แล้ว
- [ ] ตรวจสอบ Backward Compatibility แล้ว
- [ ] ทดสอบบน Environment ที่เหมาะสมแล้ว
- [ ] มี Reviewer ตาม Branch Protection Rules

## CI/CD Pipeline

| Branch หรือ Event | Lint | Test | Type Check | Security Scan | Build | Deploy |
|---|---:|---:|---:|---:|---:|---|
| Pull Request | ✅ | ✅ | ✅ | ✅ | ✅ | Preview |
| `develop` | ✅ | ✅ | ✅ | ✅ | ✅ | Staging |
| `main` | ✅ | ✅ | ✅ | ✅ | ✅ | Production |
| `hotfix/*` | ✅ | ✅ | ✅ | ✅ | ✅ | Preview |

Pipeline ควรทำงานตามลำดับดังนี้:

1. ตรวจสอบรูปแบบและคุณภาพของ Code
2. รัน Unit Test และ Integration Test
3. ตรวจสอบ Type
4. ตรวจสอบ Dependencies และ Vulnerabilities
5. สแกน Secret
6. Build Docker Image
7. สแกน Container Image
8. Deploy ไปยัง Environment ที่กำหนด
9. รัน Smoke Test หลัง Deploy
10. แจ้งผลลัพธ์ให้ทีมทราบ

> ไม่ควร Push Docker Image หรืออัปโหลดไฟล์ไป Production จาก Feature Branch โดยตรง เว้นแต่เป็น Preview Environment ที่แยกสิทธิ์และทรัพยากรไว้อย่างชัดเจน

## Environment

| Environment | Branch | วัตถุประสงค์ | ข้อมูล |
|---|---|---|---|
| Development | Local / `feature/*` | พัฒนาและ Debug | Mock หรือข้อมูลทดสอบ |
| Preview | Pull Request | ตรวจสอบการเปลี่ยนแปลง | Isolated Test Data |
| Staging | `develop` | Integration และ UAT | Staging Data |
| Production | `main` | ให้บริการจริง | Production Data |

ข้อกำหนดด้าน Environment:

- ห้ามใช้ Production Secret ใน Development หรือ Preview
- ห้ามใช้ Production Data ใน Environment อื่นโดยไม่ทำ Data Masking
- ต้องแยก Database และ Storage ตาม Environment
- ใช้ Secret Manager แทนการเก็บ Secret ใน Repository
- ต้องตรวจสอบและบันทึก Database Migration
- ควรกำหนด Approval ก่อน Deploy Production

## Commit Convention

| Type | ใช้สำหรับ |
|---|---|
| `feat` | เพิ่มความสามารถใหม่ |
| `fix` | แก้ไขข้อผิดพลาด |
| `docs` | แก้ไขเอกสาร |
| `refactor` | ปรับโครงสร้างโดยไม่เปลี่ยนพฤติกรรม |
| `test` | เพิ่มหรือแก้ไข Test |
| `perf` | ปรับปรุงประสิทธิภาพ |
| `chore` | งานบำรุงรักษาหรือการตั้งค่า |
| `ci` | แก้ไข CI/CD Workflow |
| `build` | แก้ไข Build หรือ Dependencies |
| `revert` | ย้อนการเปลี่ยนแปลง |

รูปแบบมาตรฐาน:

```text
<type>(<scope>): <description>
```

ตัวอย่าง:

```text
feat(auth): add JWT authentication
fix(api): handle invalid request payload
docs(readme): update installation guide
test(users): add repository tests
ci(github): add security scanning
```

## Release Process

เมื่อ `develop` ผ่านการทดสอบและพร้อมปล่อย:

```bash
git switch develop
git pull --ff-only origin develop

git switch -c release/1.2.0
git push -u origin release/1.2.0
```

ขั้นตอน Release:

1. ตรวจสอบ Changelog
2. ตรวจสอบ Application Version
3. รัน Full Test Suite
4. Deploy ไปยัง Staging
5. ทำ UAT และ Smoke Test
6. เปิด PR เข้า `main`
7. Merge หลังได้รับอนุมัติ
8. สร้าง Release Tag
9. Deploy Production
10. Mergeการเปลี่ยนแปลงกลับเข้า `develop`

สร้าง Release Tag:

```bash
git switch main
git pull --ff-only origin main

git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

รูปแบบ Version:

```text
vMAJOR.MINOR.PATCH
```

- `MAJOR`: มี Breaking Change
- `MINOR`: เพิ่มความสามารถที่ยัง Backward Compatible
- `PATCH`: แก้ไขข้อผิดพลาดหรือปรับปรุงเล็กน้อย

## Hotfix Process

ใช้เมื่อ Production มีปัญหาที่ต้องแก้ไขอย่างเร่งด่วน:

```bash
git switch main
git pull --ff-only origin main

git switch -c hotfix/critical-auth-error
```

ขั้นตอน:

1. สร้าง Branch จาก `main`
2. แก้ไขเฉพาะปัญหาที่จำเป็น
3. เพิ่ม Regression Test
4. เปิด PR เข้า `main`
5. ผ่าน CI และการอนุมัติเร่งด่วน
6. Merge และสร้าง Patch Release
7. Deploy Production
8. Merge Hotfix กลับเข้า `develop`

ตัวอย่าง:

```bash
git tag -a v1.2.1 -m "Hotfix v1.2.1"
git push origin v1.2.1
```

## Branch Protection

### `main`

- Require Pull Request
- Require อย่างน้อย 1–2 Approvals
- Require Status Checks
- Require Branch ให้เป็นเวอร์ชันล่าสุดก่อน Merge
- Require Conversation Resolution
- Dismiss Stale Approvals
- Restrict Force Push
- Restrict Branch Deletion
- Require Signed Commits ตามนโยบายของทีม

### `develop`

- Require Pull Request
- Require CI Checks
- Require Conversation Resolution
- Restrict Force Push
- Requireอย่างน้อย 1 Approval สำหรับการเปลี่ยนแปลงสำคัญ

## การลบ Branch

ตรวจสอบ Branch ที่ Merge แล้ว:

```bash
git fetch --prune
git branch --merged develop
```

ลบ Local Branch:

```bash
git branch -d feature/user-authentication
```

ลบ Remote Branch:

```bash
git push origin --delete feature/user-authentication
```

ห้ามลบ:

- `main`
- `develop`
- Branch ที่ยังมี PR เปิดอยู่
- Branch ที่เกี่ยวข้องกับ Release หรือ Incident
- Branch ที่จำเป็นต่อการตรวจสอบย้อนหลัง

## แนวทางปฏิบัติที่แนะนำ

- ใช้ Branch ที่มีอายุสั้น
- เปิด PR ขนาดเล็กและตรวจสอบง่าย
- Update หรือ Rebase Branch ก่อน Merge
- หลีกเลี่ยงการ Merge งานที่ยังไม่เสร็จเข้า `develop`
- ใช้ Feature Flag สำหรับฟีเจอร์ที่ต้อง Merge ก่อนเปิดใช้งาน
- ใช้ Database Migration ที่ย้อนกลับได้เมื่อทำได้
- ตรวจสอบ Backward Compatibility ของ API
- ตรวจสอบ Logs และ Metrics หลัง Deploy
- เตรียม Rollback Plan สำหรับทุก Production Deployment
- เก็บ Release Notes และ Change History ให้ครบถ้วน

***

เอกสารฉบับนี้เหมาะสำหรับใช้เป็น `CONTRIBUTING.md`, `DEVELOPMENT.md` หรือแนวทางมาตรฐานสำหรับทีมพัฒนา FastAPI โดยตรง.

การอ้างอิง:
[1] Branch-Strategy-Diagram.txt https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/1064638370/25178fe3-86ad-47b6-ae1d-6f50ee810718/Branch-Strategy-Diagram.txt

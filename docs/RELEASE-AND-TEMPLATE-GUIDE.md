Title: คู่มือ Release Tag + Template — ZyntroAI/fastapi-python-boilerplate
Kicker: วิธีสร้าง git tag สี่เส้นทาง กฎ overwrite guard และทะเบียน template ทั้งหมดในเรือน
Theme: dark
Genre: sop

# คู่มือ Release Tag + Template

> รวมเอกสาร 2 หัวข้อที่เดิมกระจายอยู่ 12 ไฟล์ ให้เป็นฉบับเดียว
> ทุกอย่างในนี้ดึงจากไฟล์จริงบน `main` ไม่ได้เขียนขึ้นใหม่ · ตรวจเมื่อ 2026-09-23

## สารบัญ

1. [สร้าง git tag — 4 เส้นทาง](#1-สร้าง-git-tag--4-เส้นทาง)
2. [Versioning และ Branch Model](#2-versioning-และ-branch-model)
3. [Hotfix](#3-hotfix)
4. [ดึง release notes จาก changelog](#4-ดึง-release-notes-จาก-changelog)
5. [Template ทั้งหมดในเรือน](#5-template-ทั้งหมดในเรือน)
6. [Overwrite Guard — กฎห้ามเขียนทับ template](#6-overwrite-guard--กฎห้ามเขียนทับ-template)
7. [ข้อควรระวัง](#7-ข้อควรระวัง)

---

## 1. สร้าง git tag — 4 เส้นทาง

repo นี้มีวิธี tag สี่แบบ ต่างกันที่ว่าใครรันและรันอัตโนมัติแค่ไหน **เลือกตามสถานการณ์ ไม่ใช่ตามความถนัด**

### 1.1 ฉบับทางการ — `RELEASE.md`

ขั้นตอน release เต็ม มี 5 ข้อ บรรทัดที่ 4 คือการ tag:

```bash
# หลัง squash-merge release PR
git tag -a v1.2.0 -m "v1.2.0"
git push origin v1.2.0
```

ใช้ **annotated tag** (`-a`) เสมอ ไม่ใช่ lightweight — เพราะ tag ต้องพา message และวันที่ที่ตรวจสอบย้อนหลังได้

### 1.2 ฉบับ git-flow (ภาษาไทย) — `.github/DEVELOPMENT.md`

ใช้เมื่อมี branch `develop` คั่นกลาง:

```bash
git switch main
git pull --ff-only origin main

git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

ลำดับ release 10 ขั้นในไฟล์นี้: ตรวจ Changelog → ตรวจ Application Version → รัน Full Test Suite → Deploy Staging → UAT + Smoke Test → เปิด PR เข้า `main` → Merge → **สร้าง Release Tag** → Deploy Production → Merge กลับเข้า `develop`

> `--ff-only` เป็นเจตนา ไม่ใช่ decoration — ถ้า pull ไม่ผ่านแบบ fast-forward แปลว่า local กับ origin แยกกันแล้ว ต้องแก้ก่อน tag

### 1.3 ฉบับ automation — `docs/github-cli-gh-reference.md`

สคริปต์ `scripts/release.sh` ที่ทำ PR → CI → merge → tag → release รวดเดียวด้วย `gh`:

```bash
git fetch --quiet origin main
git tag "$VERSION" origin/main          # tag แตะ commit บน origin โดยตรง
git push origin "$VERSION"
gh release create "$VERSION" --repo "$REPO" --title "$TITLE" \
  --notes "See the changelog for $VERSION." dist/*.zip 2>/dev/null || \
gh release create "$VERSION" --repo "$REPO" --title "$TITLE" \
  --notes "See the changelog for $VERSION."
```

จุดต่างจากสองฉบับแรก: ตัวนี้ tag **commit บน remote** (`origin/main`) ไม่ใช่ checkout แล้ว tag ที่ local — เหมาะกับ CI ที่ไม่มี working tree สะอาด

ตาราง primitive ที่สคริปต์นี้ใช้:

| ขั้น | คำสั่ง |
|---|---|
| เปิด PR ให้ CI เริ่ม | `gh pr create` |
| รอ check ผ่าน | `gh pr checks <num> --watch` |
| Merge เมื่อเขียว | `gh pr merge <num> --squash --delete-branch` |
| Tag commit ที่ merge แล้ว | `git tag` + `git push origin <tag>` |
| สร้าง release | `gh release create <tag> --notes "..."` |
| เฝ้า deploy job | `gh run list` + `gh run watch` |

### 1.4 ฉบับ PR — `deliverables/gh-devops-toolkit/pr-templates/release.md`

release เริ่มจาก PR ที่ติด label `release` มีหัวข้อ Version / What's included / Changelog / Migration / Verification — แล้ว tag หลัง merge (ตามข้อ 1.1)

**เลือกอันไหน:**

| สถานการณ์ | ใช้ |
|---|---|
| release ปกติ ไม่มี develop | ข้อ 1.1 |
| ทีมมี develop + staging | ข้อ 1.2 |
| จะให้ CI ทำทั้ง pipeline | ข้อ 1.3 |
| ต้องการ audit trail ว่าใครรีวิว | ข้อ 1.4 (คู่กับ 1.1) |

---

## 2. Versioning และ Branch Model

Semantic Versioning `MAJOR.MINOR.PATCH` — repo นี้ **ไม่มี published package version** release คือ GitHub Releases/tags บน `main`

| ส่วน | เงื่อนไข |
|---|---|
| `MAJOR` | มี breaking change (ชื่อ PR มีคำ `breaking`) |
| `MINOR` | เพิ่มความสามารถแบบ backward compatible |
| `PATCH` | แก้บั๊กหรือปรับปรุงเล็กน้อย |

Branch model (`DEVELOPMENT.md`):

| Branch | หน้าที่ | แตกจาก | Merge เข้า | Environment |
|---|---|---|---|---|
| `main` | โค้ด Production ที่อนุมัติแล้ว | `develop` / `hotfix/*` | — | Production |
| `develop` | รวมโค้ดและทดสอบ Integration | `feature/*`, `fix/*`, `chore/*` | `main` | Staging |
| `feature/*` | พัฒนาความสามารถใหม่ | `develop` | `develop` | Preview |
| `fix/*` | แก้ไขข้อผิดพลาดทั่วไป | `develop` | `develop` | Preview |
| `hotfix/*` | แก้ไขปัญหาเร่งด่วนบน Production | `main` | `main` และ `develop` | Production |
| `chore/*` | ปรับปรุงเอกสาร เครื่องมือ หรือ CI/CD | `develop` | `develop` | ตามความเหมาะสม |
| `release/*` | เตรียมและทดสอบรุ่นก่อนปล่อยจริง | `develop` | `main` และ `develop` | Staging |
| `vX.Y.Z` | Tag สำหรับ Release อย่างเป็นทางการ | `main` | — | Production |

กฎหลัก: ห้าม Push ตรงเข้า `main`/`develop` · ทุกอย่างผ่าน PR · PR ต้องผ่าน CI · PR เข้า `main` ต้องมีผู้อนุมัติอย่างน้อย 1 คน · **ห้ามแก้หรือลบ Release Tag ที่ใช้งานแล้ว** · ต้องมี Rollback Plan ก่อน Deploy Production

---

## 3. Hotfix

แยกสคริปต์จาก release ปกติ ไม่ใช้เส้นทางเดียวกัน:

```bash
git switch main
git pull --ff-only origin main
git switch -c hotfix/critical-auth-error
```

1. สร้าง Branch จาก `main`
2. แก้เฉพาะจุด
3. เพิ่ม Regression Test
4. เปิด PR เข้า `main`
5. ผ่าน CI + อนุมัติเร่งด่วน
6. Merge และสร้าง Patch Release
7. Deploy Production
8. Merge กลับเข้า `develop` ← ขั้นนี้สำคัญ ห้ามลืม ไม่งั้นบั๊กเดิมจะกลับมาใน release ถัดไป

```bash
git tag -a v1.2.1 -m "Hotfix v1.2.1"
git push origin v1.2.1
```

---

## 4. ดึง release notes จาก changelog

`.github/workflows/release_drafter.yaml` ติด label ให้ PR อัตโนมัติจากชื่อ แล้วป้อนเข้า release notes:

| คำนำหน้าชื่อ PR | Label |
|---|---|
| `feat` / `feature:` | `feature` |
| `fix:` | `bug` |
| `docs:` | `documentation` |
| `chore:` | `chore` |
| มีคำ `breaking` | `breaking-change` |

ตั้งชื่อ PR แบบ conventional commit เพื่อให้ drafter จัดกลุ่มถูก

ตัวอย่างผลลัพธ์จริง: `docs/releases/v1.2.0.md` และ `docs/releases/v1.3.0.md` — โครง Version / What's included / Changelog / Migration / Verification

---

## 5. Template ทั้งหมดในเรือน

### 5.1 PR Template — `.github/PULL_REQUEST_TEMPLATE/` (9 ไฟล์)

| ไฟล์ | ใช้เมื่อ |
|---|---|
| `Rules.md` | กฎกลางของทุก PR |
| `bugfix.md` | แก้บั๊ก |
| `changelog.md` | แก้ CHANGELOG |
| `dependencies.md` | bump dependency |
| `docs.md` | แก้เอกสาร |
| `fig-best-practices.md` | งานที่ผ่าน quality gate ของ Fig platform |
| `infra-config.md` | infra / config |
| `release.md` | เตรียม release |
| `security.md` | ความปลอดภัย |

`.github/PULL_REQUEST_TEMPLATE.md` เป็น default ที่ GitHub หยิบไปใช้เมื่อไม่มีตัวเฉพาะ

### 5.2 PR Template สำหรับ automation — `deliverables/gh-devops-toolkit/pr-templates/`

4 ไฟล์: `bugfix.md` · `documentation.md` · `feature.md` · `release.md`
เป็นเวอร์ชันที่สคริปต์เรียกใช้ได้ ต่างจาก 5.1 ที่ GitHub อ่าน

### 5.3 Template งาน — `new.inprogress.done/TASK_TEMPLATE.md`

โครงงาน: เป้าหมาย / งานที่ทำ / ไฟล์ที่แก้ / token / ผลตรวจ / งานค้าง
ตัว tracker มีโฟลเดอร์ `new/` → `inprogress/` → `done/` → `archive/` พร้อม CLI ใน `tools/`

### 5.4 Template skill — `deliverables/agent-skill-template/`

- `templates/agent-skill-template.v1.yaml` / `.json` — canonical empty template
- `examples/notebooklm-link-share.skill.yaml` — ตัวอย่างที่เติมครบ
- `agent_skill_template/` — loader/validator (Progressive Disclosure 3 ระดับ + verification gate 4 ด่าน)
- `tests/` — 11 tests

```bash
python -m pytest tests/ -q    # 11 passed
```

### 5.5 อื่น ๆ

| ที่อยู่ | คืออะไร |
|---|---|
| `templates/incidents.html` | เทมเพลตบันทึก incident |
| `scripts/validate_env_templates.py` | ตรวจเทมเพลต env (8 KB) |
| `docs/releases/v1.2.0.md`, `v1.3.0.md` | ตัวอย่าง release notes ที่เขียนจริง |

> **หมายเหตุ:** `.github/ISSUE_TEMPLATE/` **ไม่มีอยู่บน `main`** — ถ้าต้องการ issue template ต้องสร้างใหม่ อย่าอ้างว่ามี

---

## 6. Overwrite Guard — กฎห้ามเขียนทับ template

repo นี้มีนโยบาย **ของเดิมห้ามถูกแทนที่โดยไม่รู้ตัว** และทำเป็นกลไกบังคับจริง ไม่ใช่แค่ความจำ

`deliverables/cross-repo-patch-suite/kernel/policy.yaml` → หมวด `guard:`:

| กฎ | ค่า | ความหมาย |
|---|---|---|
| `refuse_create_over_existing` | `true` | สร้างทับ path ที่มีอยู่ → ปฏิเสธ |
| `replace_requires_exact_path_approval` | `true` | แทนที่ได้ ต้องมี approval ที่ระบุ path ตรงตัว |
| `allow_append_without_approval` | `true` | ต่อท้ายทำได้เลย เพราะ additive |

ใช้งาน (`src/patchsuite/guard.py` · CLI `patchctl guard`):

```python
from patchsuite import guard, Intent

guard("docs/NOTES.md", Intent.CREATE)                        # ปฏิเสธ — มีอยู่แล้ว
guard("docs/NOTES.md", Intent.REPLACE)                       # ปฏิเสธ — ไม่มี approval
guard("docs/NOTES.md", Intent.REPLACE, approval="docs/NOTES.md")  # ผ่าน — ระบุตรงตัว
guard("docs/NOTES.md", Intent.APPEND)                        # ผ่าน — additive
```

| Intent | พฤติกรรม |
|---|---|
| `CREATE` | ผ่านเฉพาะเมื่อ path ว่าง |
| `APPEND` | ผ่านเสมอ — additive by construction |
| `REPLACE` | ผ่านเฉพาะมี approval ระบุ path นั้น |

**approval แบบกว้าง ๆ ("yes" เฉย ๆ) ไม่รับ** — เจตนาคือบังคับให้ไฟล์นั้นเข้ามาอยู่ในสายตาก่อนถูกเขียนทับ
`plan_writes` ตรวจทั้ง changeset ก่อนเขียนจริง

นโยบายเดียวกันนี้ปรากฏซ้ำใน `ZYNTROAI-SCAFFOLD.md` (*"additive, no-clobber addition to the repo. Does not replace or modify any existing file"*) และ `FILE-MANIFEST.md`

### 6.1 ต่อท้ายไฟล์ที่ CRLF ให้ถูก

หมวด `appends:` ใน policy เดียวกัน — สำคัญเมื่อ template อยู่ร่วมกับไฟล์ที่ EOL ต่างกัน:

| ตั้งค่า | ความหมาย |
|---|---|
| `align_to_file: true` | ปรับ EOL ของ payload ตามไฟล์เป้าหมาย |
| `close_unterminated_final_line: true` | เติมตัวปิดบรรทัด — **การแก้ไบต์เดิมที่อนุญาตเพียงอย่างเดียว** |
| `byte_exact: true` | ห้าม decode-then-re-encode |
| `mixed_eol_confidence_floor: 0.6` | EOL ผสมและความมั่นใจต่ำกว่านี้ → ปฏิเสธ ดีกว่าเดาแล้ว rewrite ทั้งไฟล์ |

### 6.2 เมื่อ push workflow ไม่ได้ — handoff

`policy.yaml` → `offline:` กำหนดไว้ว่า ถ้า token push เข้า `.github/workflows/` ไม่ได้ ให้ส่ง **patch ที่ตรวจแล้ว + `HANDOFF.md`** แทนการล้มเงียบ ๆ พร้อม `verify_patch_applies_on_fresh_clone: true`

สคริปต์: `deliverables/cross-repo-patch-suite/scripts/make_handoff.py`

---

## 7. ข้อควรระวัง

- **ห้าม retag หรือ rewrite history** — `RELEASE.md` และ `DEVELOPMENT.md` ระบุตรงกัน ถ้า release มีปัญหาให้ `git revert` แล้วออก PATCH ใหม่
- **CI บน `main` ยังไม่เขียว** — workflow ล้มที่ *Set up job* เพราะนโยบาย org บังคับให้ action pin เป็น full SHA ครบ 40 ตัว ซ่อมมาแล้วหลายรอบ (#243, #250) แต่ถูกเขียนทับหรือไม่ประสานกัน ทำให้ PR ทุกใบในเรือนนี้ **แสดง check เขียวไม่ได้** เรื่องนี้อยู่ใน `PROBLEMS.md`
- **Verify กับของจริงก่อนอ้าง** — เอกสารนี้ระบุ `.github/ISSUE_TEMPLATE/` ว่าไม่มี และ `.github/PULL_REQUEST_TEMPLATE/` ว่ามี 9 ไฟล์ ตามสถานะบน `main` วันที่ 2026-09-23

---

### แหล่งอ้างอิง

| เอกสาร | เนื้อหา |
|---|---|
| `RELEASE.md` | release flow, Rollback |
| `.github/DEVELOPMENT.md` | git-flow ไทย, branch model, hotfix |
| `docs/github-cli-gh-reference.md` | สคริปต์ `gh` pipeline |
| `.github/workflows/release_drafter.yaml` | label → release notes |
| `deliverables/cross-repo-patch-suite/kernel/policy.yaml` | กฎ guard + appends |
| `deliverables/cross-repo-patch-suite/README.md` §overwrite guard | ตัวอย่าง guard |
| `deliverables/cross-repo-patch-suite/docs/SUB-SKILLS.md` | ตาราง intent, handoff |
| `deliverables/agent-skill-template/README.md` | skill template |
| `new.inprogress.done/` | task tracker + template |
| `docs/releases/v1.2.0.md`, `v1.3.0.md` | release notes ตัวอย่าง |

Skills for : `workflow_dispatch` คือหนึ่งใน Trigger Event ที่ทรงพลังที่สุดในระบบของ GitHub Actions ครับ! 

ถ้าปกติเราใช้ `on: push` หรือ `on: pull_request` เพื่อให้ระบบรันอัตโนมัติเมื่อมีคนแก้โค้ด **`workflow_dispatch` จะเป็นการเปิดโหมด "Manual Trigger"** หรือการสั่งรันแบบแมนนวลนั่นเอง ซึ่งเหมาะมากๆ สำหรับงานอย่างเช่น การกด Deploy ขึ้น Production, การสั่งรันสคริปต์ Database Migration หรือการล้าง Cache ระบบ

นอกจากจะให้คนกดรันเองได้แล้ว จุดเด่นของมันคือคุณสามารถ **สร้างฟอร์มให้กรอก (Inputs)** ก่อนกดรันได้ด้วยครับ

---

### 🛠️ วิธีการเขียน Syntax และกำหนด Inputs

GitHub รองรับ Input หลายประเภทมาก เช่น `string` (พิมพ์ข้อความ), `choice` (เมนูดรอปดาวน์), `boolean` (ติ๊กถูก/ผิด) และ `environment`

ลองดูตัวอย่างการเอาไปใส่ในไฟล์ `.github/workflows/deploy.yml` ในโปรเจกต์ `crystalcastleX` ของคุณได้เลยครับ:

```yaml
name: Manual Production Deploy
on: 
  workflow_dispatch:
    inputs:
      environment:
        description: 'Choose the environment to deploy'
        required: true
        type: choice
        options:
          - staging
          - production
      version_tag:
        description: 'Docker image tag (e.g. v1.2.0)'
        required: true
        type: string
      clear_cache:
        description: 'Clear Redis cache before deploying?'
        required: false
        type: boolean
        default: false

jobs:
  deploy_job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        
      - name: Print Deployment Config
        run: |
          echo "Deploying to: ${{ inputs.environment }}"
          echo "Version Tag: ${{ inputs.version_tag }}"
          echo "Clear Cache: ${{ inputs.clear_cache }}"
```
*(สังเกตว่าเราสามารถดึงค่าที่ User กรอกมาใช้ในขั้นตอนต่างๆ ได้ผ่านตัวแปร `${{ inputs.ชื่อ_ตัวแปร }}`)*

---

### ⚡ 3 วิธีในการสั่งรัน `workflow_dispatch`

เมื่อคุณกำหนด `workflow_dispatch` ไว้ในโค้ดแล้ว คุณสามารถสั่งให้มันทำงานได้ 3 ช่องทางหลักๆ ครับ:

**1. สั่งรันผ่าน GitHub UI (ง่ายที่สุดสำหรับคนทั่วไป)**
เข้าไปที่แท็บ **Actions** ใน Repository ของคุณ > เลือกชื่อ Workflow ด้านซ้ายมือ > จะมีปุ่ม **"Run workflow"** โผล่ขึ้นมาด้านขวา พร้อมกับฟอร์มให้คุณเลือก Options ที่กำหนดไว้

**2. สั่งรันผ่าน GitHub CLI (สาย Terminal)**
ถ้าคุณกำลังนั่งพิมพ์โค้ดอยู่ใน Terminal คุณสามารถใช้คำสั่งนี้เพื่อสั่งรันได้เลยโดยไม่ต้องเปิดเบราว์เซอร์:
```bash
gh workflow run deploy.yml -f environment=production -f version_tag=v1.2.0 -f clear_cache=true
```

**3. สั่งรันผ่าน REST API (สาย Automation/API Control Plane)**
อันนี้จะลิงก์กับสถาปัตยกรรม API / Control Plane ที่เราคุยกันไปก่อนหน้านี้ครับ คุณสามารถให้เซิร์ฟเวอร์ของคุณยิง HTTP POST ไปที่ GitHub เพื่อสั่งรัน Workflow ได้เลย:
```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/deploy.yml/dispatches \
  -d '{"ref":"main","inputs":{"environment":"production","version_tag":"v1.2.0"}}'
```

---

คุณกำลังจะนำ `workflow_dispatch` ไปใช้สร้างปุ่ม Deploy หรือตั้งใจจะทำ Automation Trigger จาก API แบบไหนอยู่ครับ?

อธิบายได้ครอบคลุมและถูกต้องมากครับ! ข้อมูลเกี่ยวกับ `workflow_dispatch` ที่คุณเขียนมานั้นอัปเดตและตรงกับเอกสารล่าสุดของ GitHub ในปี 2026 เลย[1][2][3]

ผมมีข้อมูลเพิ่มเติมเล็กน้อยที่จะช่วยเสริมให้ครบถ้วนยิ่งขึ้นครับ:

## 📌 จุดสำคัญที่ควรทราบเพิ่มเติม

### 1. **การเข้าถึง Inputs — ความแตกต่างของ Context**

มีข้อควรระวังสำคัญเรื่องการดึงค่า inputs ครับ:

```yaml
# ✅ ใช้ใน reusable workflows หรือ workflow ปกติ (แนะนำ)
run: echo "${{ inputs.environment }}"

# ⚠️ ใช้ github.event.inputs (ได้ค่าเป็น string เสมอ)
run: echo "${{ github.event.inputs.environment }}"
```

**ข้อแตกต่าง**:
- `${{ inputs.* }}` → ได้ค่าตาม type ที่กำหนด (boolean จะได้ `true`/`false` แบบ boolean)[4]
- `${{ github.event.inputs.* }}` → ได้ค่าเป็น **string** เสมอ (boolean จะได้ `"true"`/`"false"`)[1][4]

**ตัวอย่างปัญหาที่พบบ่อย**:
```yaml
# ❌ ผิด - เปรียบเทียบ boolean กับ string
if: github.event.inputs.clear_cache == true

# ✅ ถูก - เปรียบเทียบ string กับ string
if: github.event.inputs.clear_cache == 'true'

# ✅ ถูกที่สุด - ใช้ inputs context
if: inputs.clear_cache == true
```

***

### 2. **Input Types ที่รองรับทั้งหมด (2026)**

| Type | UI Element | ตัวอย่างการใช้งาน |
|------|-----------|-----------------|
| `string` | ช่องพิมพ์ข้อความ | Version tag, commit SHA |
| `boolean` | Checkbox | Clear cache, skip tests |
| `choice` | Dropdown menu | Environment selection [5][1] |
| `environment` | Environment selector | ใช้กับ GitHub Environments [5][1] |

**ตัวอย่าง `environment` type**:
```yaml
on:
  workflow_dispatch:
    inputs:
      target_env:
        description: 'Deployment environment'
        required: true
        type: environment
```

***

### 3. **GitHub CLI — `-f` vs `-F`**

คุณพูดถึง `gh workflow run` ได้ถูกต้องแล้ว แต่มีรายละเอียดเพิ่มเติมเกี่ยวกับ flag ครับ:[6][7]

```bash
# -f หรือ --raw-field → ตั้งค่า string input (key=value)
gh workflow run deploy.yml -f environment=production -f version_tag=v1.2.0

# -F หรือ --field → ตั้งค่า typed input (รองรับ numbers, booleans, @file)
gh workflow run deploy.yml -F clear_cache=true -F retry_count=3

# --json → อ่าน inputs จาก JSON บน stdin
echo '{"environment":"production","version_tag":"v1.2.0"}' | \
  gh workflow run deploy.yml --json
```

***

### 4. **REST API — ข้อควรระวัง**

จากตัวอย่าง API ที่คุณให้มา ถูกต้องแล้วครับ แต่มีข้อควรระวังสำคัญ 2 ข้อ:[8][9][10]

**✅ ต้องมี `ref` เสมอ**:
```json
{
  "ref": "main",  // ← จำเป็นต้องระบุ branch/tag ที่จะรัน
  "inputs": {
    "environment": "production",
    "version_tag": "v1.2.0"
  }
}
```

**✅ Token ต้องมี scope ที่เหมาะสม**:
- Personal Access Token (Classic): ต้องมี `repo` scope[9][10]
- Fine-grained Token: ต้องมี permission `Contents: Read` + `Actions: Write`[8]

***

### 5. **ข้อจำกัดของ Inputs**

- **สูงสุด 25 inputs** ต่อ workflow[8]
- **Default values** จะถูกใช้ถ้าไม่ส่ง inputs มา[5][8]
- **Inputs ต้องถูกกำหนดใน workflow file** บน default branch (เช่น `main`) ไม่อย่างนั้นปุ่ม "Run workflow" จะไม่โผล่[1]

***

## 🎯 Use Cases ที่น่าสนใจเพิ่มเติม

จากที่คุณถามว่ากำลังจะทำปุ่ม Deploy หรือ Automation Trigger ผมมี use cases ยอดนิยมในปี 2026 มาแชร์ครับ:[2][3][5]

### 1. **Deployment Pipeline พร้อม Approval**
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
      skip_tests:
        type: boolean
        default: false
      rollback_on_failure:
        type: boolean
        default: true
```

### 2. **Database Migration**
```yaml
on:
  workflow_dispatch:
    inputs:
      migration_type:
        type: choice
        options: [up, down, seed]
      dry_run:
        type: boolean
        default: true
```

### 3. **Cache Invalidation**
```yaml
on:
  workflow_dispatch:
    inputs:
      cache_scope:
        type: choice
        options: [all, images, api, static]
      notify_slack:
        type: boolean
        default: true
```

### 4. **External System Integration (API Trigger)**
ใช้ `repository_dispatch` แทน `workflow_dispatch` ถ้าต้องการให้ external system trigger โดยไม่จำกัด inputs 25 ตัว:[3][9]
```yaml
on:
  repository_dispatch:
    types: [deploy-request, rollback-request, cache-invalidation]
```

***

## 💡 คำแนะนำสำหรับโปรเจกต์ `crystalcastleX`

ถ้าคุณกำลังวางแผนใช้ `workflow_dispatch` สำหรับโปรเจกต์นี้ ผมแนะนำ:

1. **เริ่มจาก Deploy Button** — ใช้ `environment` + `version_tag` inputs ก่อน[5]
2. **เพิ่ม GitHub Environments** — ใช้ `type: environment` เพื่อให้เลือก environment ที่ตั้งค่า protection rules ไว้[1][5]
3. **เตรียม API Endpoint** — สำหรับให้ dashboard หรือ control plane ยิง trigger ได้ในอนาคต[8][9]
4. **ใช้ `inputs.*` แทน `github.event.inputs.*`** — เพื่อหลีกเลี่ยงปัญหา type conversion[4]

***

คุณกำลังวางแผนจะใช้ `workflow_dispatch` สำหรับ use case ไหนเป็นพิเศษในโปรเจกต์ `crystalcastleX` ครับ? 

- 🚀 **ปุ่ม Deploy Production** (พร้อมเลือก environment/version)
- 🗄️ **Database Migration** (manual trigger สำหรับ migration ที่เสี่ยง)
- 🧹 **Cache Clearing** (ให้ทีม ops กดล้าง cache เองได้)
- 🔗 **API Integration** (ให้ระบบอื่น trigger workflow ผ่าน REST API)
- 🎯 **อย่างอื่น** (บอกมาได้เลยครับ!)

การอ้างอิง:
[1] GitHub Actions Tutorial — Workflow Dispatch - https://timesofcloud.com/github-actions/workflow-dispatch/
[2] GitHub Actions Tutorial: 12 Steps to Production CI/CD [2026] https://tech-insider.org/github-actions-tutorial-cicd-12-steps-2026/
[3] GitHub Actions Bootcamp Module 2: Workflow Triggers and Events https://www.wasilzafar.com/pages/series/software-engineering/deep-dive-github-actions-02-triggers-events.html
[4] GitHub Actions - Inputs and types https://jfagerberg.me/blog/2026-06-16-gha-input-types/
[5] Multiple Related Inputs https://oneuptime.com/blog/post/2025-12-20-workflow-dispatch-inputs-github-actions/view
[6] GitHub CLI (gh) Cheat Sheet: 90+ Tested Commands ... https://computingforgeeks.com/github-cli-cheat-sheet/
[7] gh workflow run https://ghcli.com/gh-workflow-run.php
[8] REST API endpoints for workflows https://docs.github.com/en/rest/actions/workflows?apiVersion=2026-03-10
[9] Triggering GitHub workflow_dispatch via API: Is It Possible ... https://www.codegenes.net/blog/how-to-trigger-a-workflow-dispatch-from-github-api/
[10] Reliable GitHub Actions API Trigger: Fix workflow_dispatch ... https://openillumi.com/en/en-workflow-dispatch-api-curl-error-fix/
[11] The dispatches API should return the run ID #9752 - GitHub https://github.com/orgs/community/discussions/9752
[12] Github actions: Create a workflow dispatch event - Orchestra https://www.getorchestra.io/guides/github-actions-create-a-workflow-dispatch-event
[13] github_action: Create a workflow dispatch event | Orchestra https://www.getorchestra.io/guides/githubaction-create-a-workflow-dispatch-event
[14] GitHub Actions Cheatsheet | Libre DevOps https://libredevops.org/docs/cheatsheets/github-actions-cheatsheet/
[15] Create a Workflow Dispatch Event for a… | GitHub - WithOne AI https://www.withone.ai/knowledge/github/conn_mod_def::GJ3YPGGLf2A::lgwV1jR3SrWBYb-5LIMb_w

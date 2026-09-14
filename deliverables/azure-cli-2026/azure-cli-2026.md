---
id: azure-cli-2026
title: Azure CLI 2026 — บัตรคำ & ชีทสรุป
tags: [azure, cli, devops, jmespath, ci-cd, cheatsheet]
created: 2026-09-09
updated: 2026-09-09
related: [workflow-commands-reference, docs-readme, deliverables-readme]
summary: บัตรคำและชีทสรุปย่อสำหรับทบทวน Azure CLI 2026 ครอบคลุมการติดตั้ง, การเข้าสู่ระบบ, JMESPath, ส่วนขยาย, CI/CD และความปลอดภัย
---

# Azure CLI 2026 — บัตรคำ & ชีทสรุป

## การติดตั้ง & เวอร์ชัน

```bash
# ติดตั้ง
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
# ตรวจสอบ
az --version
# อัปเดต
az upgrade
```

## การเข้าสู่ระบบ & ความปลอดภัย ⚠️สำคัญ 2026

- ปกติ: `az login` (เบราว์เซอร์)
- ไม่มี GUI: `az login --use-device-code`
- ✅ แนะนำ: `az login --identity` (Managed Identity — ไม่เก็บโทเค็น)
- ตรวจสอบ: `az account show`, `az ad signed-in-user show`

## รูปแบบผลลัพธ์ & โครงสร้างคำสั่ง

- รูปแบบ: `json` (ค่าเริ่มต้น), `table` (อ่านง่าย), `tsv` (สคริปต์), `none` (เงียบ)
- โครงสร้าง: `az <กลุ่ม> <กลุ่มย่อย> <คำสั่ง> [อาร์กิวเมนต์]`
- ตัวอย่าง: `az vm create`, `az group list`

## JMESPath — พื้นฐาน

```bash
# เลือกฟิลด์
az vm list --query "[].{ชื่อ:name, ตำแหน่ง:location}" --output table
# กรองสถานะ
az vm list --query "[?powerState=='VM running']"
```

## JMESPath — ขั้นสูง

```bash
# เรียง
az group list --query "sort_by(@, &name)"
# นับ
az vm list --query "length(@)"
# ซ้อน
az vm list --query "[].{ขนาด:hardwareProfile.vmSize}"
```

## ส่วนขยาย (Extensions)

```bash
az extension list --output table
az extension list-available --output table
az extension add --name <ชื่อ>
az extension update --name <ชื่อ>
az extension remove --name <ชื่อ>
```

## CI/CD & GitHub Actions (OIDC)

```yaml
permissions:
  id-token: write  # สำคัญสำหรับ OIDC
uses: azure/login@v2
with:
  client-id: ${{ secrets.AZURE_CLIENT_ID }}
  tenant-id: ${{ secrets.AZURE_TENANT_ID }}
  subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## การจัดการข้อผิดพลาด & ความแตกต่าง Shell

- เงียบขึ้น: `--only-show-errors`
- ดีบัก: `az --debug <คำสั่ง>`
- ตัดบรรทัด: Bash `\` | PowerShell `` ` ``
- ตัวแปร: Bash `"$var"` | PowerShell `$var`

---

# ชีทสรุปย่อ (One-Page)

## 🔐 การตรวจสอบสิทธิ์ & บัญชี

| คำสั่ง | การใช้งาน |
|--------|-----------|
| `az login` | เข้าสู่ระบบ (โต้ตอบ) |
| `az login --identity` | Managed Identity ✅ |
| `az account show` | ดูบัญชีปัจจุบัน |
| `az account set --subscription <ID>` | เปลี่ยน Subscription |

## 📦 กลุ่มทรัพยากร

```bash
az group create --name <ชื่อ> --location <ที่ตั้ง>
az group list --output table
az group delete --name <ชื่อ> --yes
```

## 🖥️ เครื่องเสมือน (VM)

```bash
az vm create --resource-group <RG> --name <ชื่อ> --image Ubuntu2204
az vm list --output table
az vm start/deallocate/restart --resource-group <RG> --name <ชื่อ>
```

## 🔍 คิวรี JMESPath (ยอดนิยม)

| ฟังก์ชัน | ตัวอย่าง |
|----------|----------|
| เลือกฟิลด์ | `[].{ชื่อ:name, ตำแหน่ง:location}` |
| กรอง | `[?property=='ค่า']` |
| เรียง | `sort_by(@, &ฟิลด์)` |
| นับ | `length(@)` |
| ทั้งหมด | `[]` หรือ `[*]` |

## 🛡️ ความปลอดภัย 2026

- ✅ ห้าม: ใส่รหัส/โทเค็นในโค้ด
- ✅ ใช้: Key Vault (`az keyvault secret show`) + Managed Identity
- ✅ สิทธิ์: จำกัด `--scope` ให้แคบที่สุด (Least Privilege)

## ⚖️ เปรียบเทียบเครื่องมือ

- Azure CLI: ข้ามแพลตฟอร์ม, เบา, สคริปต์ได้ดี ✅
- Az PowerShell: Windows/.NET
- Cloud Shell: ในเบราว์เซอร์, ไม่ต้องติดตั้ง

---

## Related

- [[Azure]]
- [[CLI]]
- [[DevOps]]
- [[JMESPath]]
- [[Bicep]]

## ลิงก์ที่เกี่ยวข้องในโปรเจกต์

- ตัวอย่าง workflow เต็ม: `examples/azure-bicep-deploy.yml` (ในโฟลเดอร์นี้)
- คำสั่ง workflow commands: [`docs/github-actions/workflow-commands-reference.md`](../../docs/github-actions/workflow-commands-reference.md)
- ดัชนีเอกสาร: [`docs/README.md`](../../docs/README.md) · [`deliverables/README.md`](../../deliverables/README.md)


---

# ภาคผนวก Bicep / IaC (2026)

## Bicep & Infrastructure as Code — ภาพรวม

**Bicep** คือ Domain-Specific Language (DSL) ของ Microsoft สำหรับนิยาม Azure infrastructure โดยคอมไพล์เป็น ARM JSON template เดียวกัน ทำงานผ่าน Azure CLI (`az bicep`) หรือ `az deployment` — ใช้คู่กับ Azure CLI ได้ครบวงจร

## คำสั่ง `az bicep` หลัก

```bash
# build — คอมไพล์ .bicep → ARM JSON (ตรวจ syntax + lint)
az bicep build --file infra/main.bicep

# decompile — แปลง ARM JSON กลับเป็น .bicep
az bicep decompile --file template.json

# lint — ตรวจหาข้อผิดพลาด/คำแนะนำโดยไม่ build
az bicep lint --file infra/main.bicep

# publish — เผยแพร่โมดูลเป็น private module registry
az bicep publish --file modules/storage.bicep \
  --target br:myregistry.azurecr.io/bicep/modules/storage:v1
```

> ตรวจเวอร์ชัน Bicep: `az bicep version` — อัปเดต: `az bicep upgrade`

## โครงสร้างไฟล์มาตรฐาน

```
infra/
├── main.bicep            # จุดเริ่มต้น — นิยาม resource + เรียก modules
├── modules/
│   ├── storage.bicep     # โมดูลย่อยที่ใช้ซ้ำ
│   ├── appservice.bicep
│   └── keyvault.bicep
└── params/
    ├── dev.bicepparam    # แยกค่าตาม environment
    └── prod.bicepparam
```

## ตัวอย่าง `main.bicep` — Resource Group + Storage Account

```bicep
// infra/main.bicep
param location string = resourceGroup().location
param storageName string

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false      // ปิด public access (ปลอดภัย)
  }
}

output storageId string = storage.id
output storageName string = storage.name
```

## Deploy ผ่าน CLI + what-if + ความปลอดภัย

```bash
# 1) ตรวจ syntax/lint
az bicep build --file infra/main.bicep

# 2) what-if — ดูผลกระทบก่อน deploy จริง (แนะนำเสมอ)
az deployment group what-if \
  --resource-group rg-prod-01 \
  --template-file infra/main.bicep \
  --parameters storageName=stappdemo01

# 3) deploy (Incremental = ค่าเริ่มต้น ไม่ลบ resource ที่ไม่อยู่ใน template)
az deployment group create \
  --resource-group rg-prod-01 \
  --template-file infra/main.bicep \
  --parameters storageName=stappdemo01

# ลบ deployment history ที่ไม่ใช้ (กันเกินโควตา 800/RG)
az deployment group delete --resource-group rg-prod-01 --name main
```

### แนวทางปฏิบัติเพื่อความปลอดภัย

- ปิด public access เป็นค่าเริ่มต้น: Storage `allowBlobPublicAccess: false`, Key Vault `defaultAction: 'Deny'`
- Secrets: ใช้ `@secure()` + ดึงผ่าน Key Vault (`az keyvault secret show`) — ไม่ hardcode
- Key Vault: เปิด `enableRbacAuthorization` (RBAC แทน access policy), soft-delete 90 วัน
- ใช้ `uniqueString()` ต่อท้ายชื่อ resource ที่ต้อง unique ระดับ global
- ทำ `what-if` ก่อน `create` ทุกครั้งใน environment ที่ไม่ใช่ dev

---


## การทำงานร่วมกับ GitHub Actions Workflow Commands

Workflow ใช้ `azure/login@v2` (OIDC) เพื่อให้คำสั่ง `az` รันโดยไม่ต้องเก็บ secret และใช้ **workflow commands** เพื่อพับ/บันทึกผล:

```bash
# ::group:: / ::endgroup:: — จัดกลุ่ม log ให้อ่านง่าย
echo "::group::Azure Deployment"
az deployment group create ...  # ขั้นตอนจริง
echo "::endgroup::"

# ::notice:: — แสดงข้อความระดับ notice
echo "::notice title=Deployment::Succeeded for $(az account show --query name -o tsv)"

# ::warning:: / ::error:: — annotation บนไฟล์/ขั้นตอน
echo "::warning file=infra/main.bicep,line=12::Resource name not unique"
echo "::error title=Deploy Failed::Check what-if output"

# เขียนผลลัพธ์สู่ $GITHUB_ENV / $GITHUB_OUTPUT / $GITHUB_STEP_SUMMARY
echo "RG_NAME=rg-prod-01" >> "$GITHUB_ENV"
echo "storage_id=$(az deployment group show ... )" >> "$GITHUB_OUTPUT"

# สรุปผลใน PR / Job ผ่าน Markdown
cat <<'EOF' >> "$GITHUB_STEP_SUMMARY"
## Azure Deployment ✅
- **Resource Group:** `rg-prod-01`
- **Storage:** `stappdemo01`
EOF
```

> ดูคำสั่ง workflow ครบได้ที่ `docs/github-actions/workflow-commands-reference.md`

## ตัวอย่าง end-to-end workflow (`azure-bicep-deploy.yml`)

```yaml
# .github/workflows/azure-bicep-deploy.yml
name: Azure Bicep Deploy
on:
  push:
    branches: [main]
    paths: ['infra/**']
  workflow_dispatch:

permissions:
  id-token: write   # จำเป็นสำหรับ OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # เข้าสู่ระบบ Azure ด้วย OIDC — ไม่เก็บ client secret
      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Lint Bicep
        run: az bicep build --file infra/main.bicep

      - name: What-if (preview)
        run: |
          echo "::group::What-if"
          az deployment group what-if \
            --resource-group rg-prod-01 \
            --template-file infra/main.bicep
          echo "::endgroup::"

      - name: Deploy
        id: deploy
        run: |
          az deployment group create \
            --resource-group rg-prod-01 \
            --template-file infra/main.bicep
          echo "storage=$(az deployment group show ... --query properties.outputs.storageName.value -o tsv)" >> "$GITHUB_OUTPUT"

      - name: Job summary
        if: always()
        run: |
          cat <<'EOF' >> "$GITHUB_STEP_SUMMARY"
          ## Deploy Result
          Storage: `${{ steps.deploy.outputs.storage }}`
          EOF
```

> ⚠️ ตัวอย่างใช้ `actions/checkout@v4` / `azure/login@v2` เป็น **tag** เพื่อให้อ่านง่าย — ตาม policy ของ repo นี้ต้องใช้ **full SHA** ก่อน deploy จริง

---

---
id: azure-cli-2026
title: Azure CLI 2026 — บัตรคำ & ชีทสรุป
tags: [azure, cli, devops, jmespath, ci-cd, cheatsheet]
created: 2026-09-09
updated: 2026-09-09
related: []
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

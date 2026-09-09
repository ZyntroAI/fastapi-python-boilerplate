// deliverables/azure-cli-2026/examples/bicepparam/dev.bicepparam
// ตัวอย่าง parameter file (dev) — ปรับบรรทัด `using` ให้ชี้ main.bicep จริงของโปรเจกต์คุณ
// เช่น: using '../../../infra/main.bicep'
using '../main.bicep'

param location = 'southeastasia'
param storageName = 'stappdev01'
param appServicePlanSku = 'F1'        // Free tier สำหรับ dev
param environment = 'dev'

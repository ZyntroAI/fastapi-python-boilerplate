// deliverables/azure-cli-2026/examples/bicepparam/prod.bicepparam
// ตัวอย่าง parameter file (prod) — ปรับบรรทัด `using` ให้ชี้ main.bicep จริงของโปรเจกต์คุณ
using '../main.bicep'

param location = 'southeastasia'
param storageName = 'stappprod01'
param appServicePlanSku = 'P1v2'      // Premium สำหรับ prod
param environment = 'prod'

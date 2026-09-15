# FIG Architecture

## FIG v4.0 — Enterprise

FIGURE ถูกวางเป็นสถาปัตยกรรมระดับ Enterprise ประกอบด้วย 13 องค์ประกอบ:

| # | Component | หน้าที่ |
|---|---|---|
| 1 | API Gateway | ประตูเข้า API ทั้งหมด |
| 2 | API Registry | ทะเบียน API |
| 3 | API SDK | ชุดเรียกใช้ API ฝั่ง client |
| 4 | CRUD Engine | สร้าง/อ่าน/แก้/ลบ |
| 5 | MasterFiles Engine | ไฟล์ต้นทางที่ควบคุมสิทธิ์ |
| 6 | RBAC | สิทธิ์ตามบทบาท |
| 7 | Permission Middleware | ตรวจสิทธิ์ต่อ request |
| 8 | Retry Engine | ลองซ้ำเมื่อล้มเหลว |
| 9 | Cache Engine | แคช |
| 10 | Audit Logger | บันทึกการใช้งาน |
| 11 | Metrics | ตัวชี้วัด |
| 12 | JWT Manager | ออก/ตรวจ token |
| 13 | Plugin System | ส่วนขยาย |

ค่าจริง: `config/fig.components.json`

## FIG v4.1 — Organization Edition

เมื่อผูกกับ Organization **ZyntroAI** FIG ยกระดับเป็น:

```text
ZyntroAI Organization
│
├── FIG-Core
│
├── FIG-API
│
├── FIG-MasterFiles
│
├── FIG-Plugins
│
├── FIG-Security
│
├── FIG-Docs
│
└── .github
```

ความสามารถที่เพิ่มจาก v4.0:

```text
FIG v4.1 Organization Edition

Frontend Framework
+ API Gateway
+ API SDK
+ MasterFiles Engine
+ Enterprise Security Layer
+ Organization Governance
+ GitHub Owner Control
+ Audit Platform
+ Plugin Ecosystem
```

โครงนี้รองรับการควบคุมหลาย Repository ภายใต้ Organization Owner เดียว
และขยายต่อเป็น Enterprise Platform ได้ในอนาคต

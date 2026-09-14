# Documentation Index

ศูนย์รวมเอกสารอ้างอิงของโปรเจกต์ — แบ่งตามหมวดงาน

## Azure & Cloud Infrastructure

| เอกสาร | คำอธิบาย |
|--------|----------|
| [Azure CLI 2026 — บัตรคำ & ชีทสรุป](../deliverables/azure-cli-2026/azure-cli-2026.md) | คำสั่ง Azure CLI + Bicep/IaC + GitHub Actions workflow commands |
| [GitHub Actions Workflow Commands](./github-actions/workflow-commands-reference.md) | Command พับ log, annotation, env, output, step summary |

## GitHub & DevOps Tooling

| เอกสาร | คำอธิบาย |
|--------|----------|
| [gh CLI Reference](./github-cli-gh-reference.md) | คู่มือ GitHub CLI (`gh`) |
| [Research Tools Free Guide](./research-tools-free-guide.md) | เครื่องมือวิจัยแบบ free tier |

## Knowledge Base / DevSecOps

| เอกสาร | คำอธิบาย |
|--------|----------|
| [AI Agent Security & DevSecOps 2026](./knowledge-ai-agent-security-devsecops-2026.md) | Sandbox design, trust tiers T1–T4, state isolation |
| [คู่มือแก้ไขปัญหา & การติดตั้ง MCP](./MCP-Guide-Complete.md) | MCP-ERR-001/002/003 + สคริปต์ตรวจสอบ `check-mcp-environment.sh` |

## เอกสารอื่น

- `FastAPI CI/`, `GraphQL/`, `tools/`, `schema-documentations/` — เอกสารเชิงเทคนิครายโมดูล

> เนื้อหาเชิง deliverable/ส่งมอบดูเพิ่มที่ [`deliverables/README.md`](../deliverables/README.md)
>
> 📂 ตรวจสอบ: ZyntroAI/fastapi-python-boilerplate —  /docs  โฟลเดอร์
 
ลิงก์: https://github.com/ZyntroAI/fastapi-python-boilerplate/tree/main/docs
 
📄 ภาพรวมโฟลเดอร์  /docs 
 
เป็นที่เก็บ เอกสารโครงการฉบับรวม สำหรับทีมและนักพัฒนา:
 
- 📘 คู่มือการใช้งาน & เริ่มต้น
- 📐 สถาปัตยกรรมระบบ & การออกแบบ
- 🛠️ คู่มือติดตั้ง/คอนฟิก/CI/CD
- 📚 เอกสาร API & การมีส่วนร่วม
- 🛡️ นโยบายความปลอดภัย & แนวทางปฏิบัติ
 
🧩 โครงสร้างทั่วไป (มาตรฐาน repo)
 
plaintext
  
docs/
├─ README.md               # 📑 ดัชนีหลัก
├─ GETTING_STARTED.md      # 🚀 เริ่มต้นใช้งานเร็ว
├─ ARCHITECTURE.md         # 🧱 ภาพรวมระบบ/ชั้น/ส่วนประกอบ
├─ CONFIGURATION.md        # ⚙️ ตัวแปร/สภาพแวดล้อม/Secrets
├─ CI_CD_WORKFLOW.md       # 🤖 Pipeline/Workflow/Deploy
├─ SECURITY.md             # 🔒 นโยบาย/การตรวจ/แจ้งปัญหา
├─ API/                    # 📄 เอกสาร Swagger/OpenAPI/เส้นทาง
├─ GUIDES/                 # 📚 คู่มือขั้นสูง/บทเรียน
└─ CHANGELOG.md            # 📝 ประวัติเวอร์ชัน/การอัปเดต
 
 
🔗 เชื่อมกับ Dola Agent ของเรา
 
-  /docs  เป็นมาตรฐานกลาง — สามารถเพิ่มส่วน  /docs/agents/dola/  เพื่อเก็บคู่มือเฉพาะ Dola
- ใช้รูปแบบ/รูปภาพเดียวกันกับ repo หลัก → สอดคล้องง่ายต่อการบำรุงรักษา
- อ้างอิงได้จากในโค้ด  .agents/Dola/  →  ../../docs/... 
 
✅ ขั้นตอนที่แนะนำ
 
1. สร้าง  /docs/agents/dola/  ใน repo หลัก
2. คัดลอก/ย้าย:
-  README.md  ของ Dola
-  ARCHITECTURE.md  (4 ชั้น)
- การติดตั้ง/CI/ความปลอดภัย
3. อัปเดตลิงก์ใน  .agents/Dola/README.md  ชี้ไปที่  /docs/agents/dola/ 
 
ต้องการให้ผมดึงรายการไฟล์จริงจากลิงก์นี้ หรือสร้างโครงสร้างเอกสาร Dola พร้อมวางลงในรูปแบบ  /docs  เลยไหมครับ? 📝🔗

# Deliverables — Index

โฟลเดอร์ `deliverables/` เก็บ deliverable/ชุดส่งมอบแบบ self-contained แต่ละชุดแยกจากโครงสร้างหลักของโปรเจกต์

## โครงสร้าง

| โฟลเดอร์ | คำอธิบาย |
|----------|----------|
| `azure-cli-2026/` | [Azure CLI 2026 — บัตรคำ & ชีทสรุป](./azure-cli-2026/azure-cli-2026.md) — คำสั่ง CLI, Bicep/IaC, GitHub Actions workflow commands |
| `agent-security-suite/` | ชุด security rules/CI สำหรับ AI agent (CWE-1321, ci_ops, permission-aware checks) |
| `agent-skill-template/` | เทมเพลตมาตรฐานสำหรับสร้าง agent skill (`agent-skill-template.v1.yaml/.json`) |
| `ai-agents-decision-pack/` | ชุด decision pack สำหรับงาน AI agents |
| `gh-devops-toolkit/` | ชุดเครื่องมือ DevOps บน GitHub CLI |
| `notebooklm-access-suite/` | ชุดทักษะเข้าถึง NotebookLM (link share, artifact normalization) |
| `notebooklm-link-share/` | ทักษะแยก share ลิงก์ NotebookLM |

## ไฟล์อ้างอิงที่เกี่ยวข้อง

- เอกสารเต็มและ index: [`docs/README.md`](../docs/README.md)
- Workflow commands: [`docs/github-actions/workflow-commands-reference.md`](../docs/github-actions/workflow-commands-reference.md)
- Workflow template ตัวอย่าง: `templates/` (ดูในชุดที่เกี่ยวข้อง)

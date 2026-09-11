# Deliverables — Index

โฟลเดอร์ `deliverables/` เก็บ deliverable/ชุดส่งมอบแบบ self-contained แต่ละชุดแยกจากโครงสร้างหลักของโปรเจกต์

## โครงสร้าง

| โฟลเดอร์ | คำอธิบาย |
|----------|----------|
| `gemini-cli-skills/` | [Gemini CLI — docs & skills architecture](./gemini-cli-skills/README.md) — research brief, AGENTS/SKILLS index, ZyntroAI skill overlay templates |
| `azure-cli-2026/` | [Azure CLI 2026 — บัตรคำ & ชีทสรุป](./azure-cli-2026/azure-cli-2026.md) — คำสั่ง CLI, Bicep/IaC, GitHub Actions workflow commands |
| `agent-security-suite/` | ชุด security rules/CI สำหรับ AI agent (CWE-1321, ci_ops, permission-aware checks) |
| `agent-skill-template/` | เทมเพลตมาตรฐานสำหรับสร้าง agent skill (`agent-skill-template.v1.yaml/.json`) |
| `ai-agents-decision-pack/` | ชุด decision pack สำหรับงาน AI agents |
| `gh-devops-toolkit/` | ชุดเครื่องมือ DevOps บน GitHub CLI |
| `notebooklm-access-suite/` | ชุดทักษะเข้าถึง NotebookLM (link share, artifact normalization) |
| `ai-gateway-architecture-review/` | [AI Gateway Architecture Review — resilience & cost control](./ai-gateway-architecture-review/README.md) — Risk Register 32 จุดอ่อน, สถาปัตยกรรมที่ปรับปรุง (M1–M21), rollout 6 ระยะ |
| `notebooklm-link-share/` | ทักษะแยก share ลิงก์ NotebookLM |
| `pm-backend/` | [Program Management Backend](./pm-backend/README.md) — FastAPI app 4 modules: PM CSV template, provider-neutral billing (stub/Stripe/Chargebee/Paddle), tool switcher, opt-in encryption at rest |
| `agent-core/` | [Agent Core](./agent-core/README.md) — provider-agnostic agent task backend: async httpx client, bounded retry + polling, Supabase task store with RLS, FastAPI routes (25 tests) |
| `product-crud/` | [Products CRUD](./product-crud/README.md) — Prisma `Product` + Express (Zod → service → controller → routes) และ React + TanStack Query (search/pagination state อยู่ใน query key, 30 tests) |

## ไฟล์อ้างอิงที่เกี่ยวข้อง

- เอกสารเต็มและ index: [`docs/README.md`](../docs/README.md)
- Workflow commands: [`docs/github-actions/workflow-commands-reference.md`](../docs/github-actions/workflow-commands-reference.md)
- Workflow template ตัวอย่าง: `templates/` (ดูในชุดที่เกี่ยวข้อง)

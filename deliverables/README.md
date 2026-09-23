# Deliverables — Index

โฟลเดอร์ `deliverables/` เก็บ deliverable/ชุดส่งมอบแบบ self-contained แต่ละชุดแยกจากโครงสร้างหลักของโปรเจกต์

มีทั้งหมด **31 ชุด** เรียงตามตัวอักษร:

| โฟลเดอร์ | คำอธิบาย |
|----------|----------|
| `agent-core/` | [Agent Core](./agent-core/README.md) — provider-agnostic agent task backend: async httpx client, bounded retry + polling, Supabase task store with RLS, FastAPI routes (25 tests) — with Dockerfile (digest-pinned, non-root) + Helm chart (read-only rootfs, secret-ref, HPA/ingress) |
| `agent-security-suite/` | ชุด security rules/CI สำหรับ AI agent (CWE-1321, ci_ops, permission-aware checks) |
| `agent-skill-template/` | เทมเพลตมาตรฐานสำหรับสร้าง agent skill (`agent-skill-template.v1.yaml/.json`) |
| `ai-agent-skills/` | [AI Agent Skills Bundle](./ai-agent-skills/README.md) — ชุด 20 agent skills + AI Context engine (progressive disclosure, least-privilege scopes, matcher/router, 13 tests) |
| `ai-agents-decision-pack/` | ชุด decision pack สำหรับงาน AI agents |
| `ai-gateway-architecture-review/` | [AI Gateway Architecture Review — resilience & cost control](./ai-gateway-architecture-review/README.md) — Risk Register 32 จุดอ่อน, สถาปัตยกรรมที่ปรับปรุง (M1–M21), rollout 6 ระยะ |
| `azure-cli-2026/` | [Azure CLI 2026 — บัตรคำ & ชีทสรุป](./azure-cli-2026/azure-cli-2026.md) — คำสั่ง CLI, Bicep/IaC, GitHub Actions workflow commands |
| `cache-reduction-skill/` | [Cache Reduction](./cache-reduction-skill/README.md) — cache-footprint audit toolkit: three independent checks over service caches |
| `ci/` | ชุด patch สำหรับ `auto-compress-manage.yml` — เงื่อนไข skip ที่ต้องวางเป็น `.github/workflows/auto-compress-manage.yml` |
| `ci-workflow-sha-pin/` | [CI Workflow SHA-Pin + YAML Repair](./ci-workflow-sha-pin/README.md) — pin ทุก `uses:` เป็น full SHA ครบ 40 ตัวตาม org ruleset + ซ่อม YAML ที่ parse ไม่ผ่าน |
| `copilot-free-actions-playbook/` | [Copilot Free + Actions Hardening Playbook](./copilot-free-actions-playbook/README.md) — near-Pro value from GitHub Copilot Free + GitHub Actions hardening (deck + auditor) |
| `cross-repo-patch-suite/` | [Cross-Repo Patch Suite](./cross-repo-patch-suite/README.md) — patch ให้ข้าม repo แล้ว byte-faithful: append ที่ไม่เขียนทับ byte เดิม, CRLF/EOL fidelity, ตรวจ workflow YAML + SHA-pin, overwrite guard (125 tests) |
| `cwe1321-protection-suite/` | [CWE-1321 Prototype Pollution Protection Suite](./cwe1321-protection-suite/README.md) — `TASK-SEC-CWE1321-001` P0: กฎ JS/Python, CI enforcement (ดู [TEST-REPORT](./cwe1321-protection-suite/TEST-REPORT.md)) |
| `dev-helpers/` | [dev-helpers](./dev-helpers/README.md) — เครื่องมือเล็ก 4 ตัวสำหรับจุดที่เจ็บที่สุดของงาน GitHub อัตโนมัติ: ตรวจคำสั่งก่อนว่า, workflow ไฟล์ไหนพัง, เขียนคำขอสิทธิ์, ประกอบ PR ให้ครบ Definition of Done |
| `docker-stack/` | [Docker stack](./docker-stack/README.md) — FastAPI + PostgreSQL + Redis ที่รันได้จริง: multi-stage Python image (non-root, tini, HEALTHCHECK), compose + optional nginx, docker targets ใน Makefile แยกไฟล์ — แก้ 2 อย่างที่ repo ไม่ได้บอก: `requirements.txt` ขาด 2 dependency ที่แอปต้องใช้ และ health path จริงคือ `/health` ไม่ใช่ `/health/` (307) |
| `docs-verify/` | [Documentation Drift Verifier](./docs-verify/README.md) — ตรวจว่า README/PROBLEMS.md/LICENSE ยังตรงกับ tree จริง: count, path, workflow parse, SHA-pin split, licence holder (17 tests) |
| `fastapi-obsidian-backend/` | [FastAPI + Obsidian Backend](./fastapi-obsidian-backend/README.md) — เสิร์ฟ Obsidian skill library เป็น REST API พร้อม JWT auth, per-user access และ opt-in encryption at rest |
| `fig-best-practices/` | [fig-best-practices](./fig-best-practices/README.md) — มาตรฐาน FIG / hellofig.ai ในรูป deliverable ที่รันได้ (ดู [BEST-PRACTICES.md](./fig-best-practices/BEST-PRACTICES.md)) |
| `firecrawl-fastapi/` | [FireCrawl + FastAPI](./firecrawl-fastapi/README.md) — เก็บข้อมูลเว็บระดับโปรดักชัน: **scrape** หน้าเว็บ + **crawl** ลิงก์ลึก ผ่าน REST API |
| `full-cicd-pipeline/` | [Full CI/CD Pipeline](./full-cicd-pipeline/README.md) — orchestrated baseline ที่ SHA-pinned ครบ (ดู [HANDOFF.md](./full-cicd-pipeline/HANDOFF.md)) |
| `gemini-cli-skills/` | [Gemini CLI — docs & skills architecture](./gemini-cli-skills/README.md) — research brief, AGENTS/SKILLS index, ZyntroAI skill overlay templates |
| `gh-devops-toolkit/` | ชุดเครื่องมือ DevOps บน GitHub CLI |
| `manus-client/` | [manus-client](./manus-client/README.md) — async client สำหรับ Manus REST API v2 แบบ task-first สร้างจาก surface จริงที่ probe กับ `api.manus.ai` |
| `notebooklm-access-suite/` | ชุดทักษะเข้าถึง NotebookLM (link share, artifact normalization) |
| `notebooklm-link-share/` | ทักษะแยก share ลิงก์ NotebookLM |
| `official-docs/` | [Official Documentation](./official-docs/README.md) — registry, components และการตรวจลิงก์ ของ official docs ที่ใช้ทั่วทั้ง repo |
| `onspace-ai/` | [OnSpaceAI](./onspace-ai/README.md) — AI reliability engine (cache, circuit breaker, fallback router, context compiler, token budget, Prometheus) เป็น standalone FastAPI app (31 tests) |
| `onspace-platform-integration/` | [OnSpace Platform Integration](./onspace-platform-integration/README.md) — ดึง OnSpaceAI engine ออกมาเป็น reusable AI infrastructure service (`OnSpaceAIService`, ไม่มี FastAPI import) + provider chain (OpenAI/Anthropic/Google/mock) + [ADR-001](./onspace-platform-integration/ADR-001-onspace-as-platform-service.md) และ [Migration Plan](./onspace-platform-integration/MIGRATION.md) (58 tests) |
| `pm-backend/` | [Program Management Backend](./pm-backend/README.md) — FastAPI app 4 modules: PM CSV template, provider-neutral billing (stub/Stripe/Chargebee/Paddle), tool switcher, opt-in encryption at rest |
| `product-crud/` | [Products CRUD](./product-crud/README.md) — Prisma `Product` + Express (Zod → service → controller → routes) และ React + TanStack Query (search/pagination state อยู่ใน query key, 30 tests) |
| `pure-agent-dev/` | [pure-agent-dev](./pure-agent-dev/README.md) — ทิศทาง dependency ที่บังคับด้วย `tests/test_architecture.py` |


## ไฟล์อ้างอิงที่เกี่ยวข้อง

- เอกสารเต็มและ index: [`docs/README.md`](../docs/README.md)
- Workflow commands: [`docs/github-actions/workflow-commands-reference.md`](../docs/github-actions/workflow-commands-reference.md)
- Workflow template ตัวอย่าง: `templates/` (ดูในชุดที่เกี่ยวข้อง)


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

## Release, Template & Repo Hygiene

| เอกสาร | คำอธิบาย |
|--------|----------|
| [Release Tag + Template Guide](./RELEASE-AND-TEMPLATE-GUIDE.md) | วิธีสร้าง git tag สี่เส้นทาง, กฎ overwrite guard และทะเบียน template ทั้งหมด |
| [Enterprise Feature Stack](./enterprise-feature-stack.md) | ชุดเอกสาร Enterprise Feature Stack (Feature Manifest, Policy Schema, Deployment Config, README-ENTERPRISE) |
| [Claude REST API](./claude-rest-api.md) | Claude REST API — knowledge & skill package |
| [Feature-flag rollback testing](./feature-flag-rollback-testing.md) | รูปแบบ deploy ครั้งเดียวแล้ว rollback ด้วย flag |
| [FIG v4 + Agent Skills + MCP compendium](./fig/fig-v4-agent-skills-mcp-compendium.md) | เอกสารรวมฉบับสมบูรณ์ FIG v4 + Agent Skills + MCP |
| [MCP guide — plan](./mcp/mcp-guide-plan.md) | แผนงานของคู่มือ MCP |
| [MCP guide — PR body](./mcp/mcp-guide-pr-body.md) | เนื้อหา PR body ของคู่มือ MCP |
| [Skills integration update](./update/skills-integration-update.md) | รายงานสถานะการผสาน Skills ecosystem |
| [FIG Drive upload test](./update/fig-drive-upload-test.md) | ผลทดสอบอัปโหลดไฟล์จาก workspace |
| [markdownlint MD009](./tools/markdownlint/md009.md) | กฎ MD009 — trailing spaces |
| [markdownlint MD032](./tools/markdownlint/md032.md) | กฎ MD032 — lists surrounded by blank lines |

> เนื้อหาเชิง deliverable/ส่งมอบดูเพิ่มที่ [`deliverables/README.md`](../deliverables/README.md)
>
> 📂 ตรวจสอบ: ZyntroAI/fastapi-python-boilerplate —  /docs  โฟลเดอร์
 


ได้เลยครับ ✅ เปรียบเทียบข้อมูลจากทั้ง 2 Repository แล้ว จัดทำ README.md ฉบับสมบูรณ์ + เอกสาร FIG Integration พร้อมโครงสร้าง Obsidian ให้เรียบร้อยแล้วครับ 🚀
 
 
 
📄 README.md — ZyntroAI/new-crystalcastle
 
markdown
  
---
title: FIG ZyntroAI CrystalCastle
version: 1.7.0-MERGED-FIG
aliases:
  - CrystalCastle
  - New CrystalCastle
tags:
  - fastapi
  - fig
  - zyntroai
  - boilerplate
  - python
  - ai-agents
created: 2026-09-29T20:00:00+07:00
source: ZyntroAI/fastapi-python-boilerplate
---

# 🏰 FIG ZyntroAI CrystalCastle — v1.7.0-MERGED-FIG

> FastAPI Production Backend • AI-Driven DevOps Stack • FIG Agent-Native

![GitHub](https://img.shields.io/badge/GitHub-ZyntroAI%2Fnew--crystalcastle-blue)
![Version](https://img.shields.io/badge/version-1.7.0--MERGED--FIG-brightgreen)
![FIG](https://img.shields.io/badge/FIG-V5.1--Balanced--Green--Biome--Solar--Dawn-purple)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)

---

## 📌 Overview

**FIG ZyntroAI CrystalCastle** — บริการ Backend API สำหรับระบบ New CrystalCastle พัฒนาด้วย FastAPI โดยเริ่มต้นจาก `ZyntroAI/fastapi-python-boilerplate` และผสานรวม **FIG AI Agent Framework** เพื่อให้ระบบสามารถรู้จักและทำงานร่วมกับ FIG Agents ได้ทันที

### 🧬 FIG Identity
| Field | Value |
|---|---|
| **Name** | FIG ZyntroAI CrystalCastle |
| **Version** | `1.7.0-MERGED-FIG` |
| **FIG Commit** | `4b0e59c7d34a7aa8053ad5286e1ee093fdb255f1` |
| **FIG Tag** | `FIG-V5.1-Balanced-Green-Biome-Solar-Dawn` |
| **FIG App ID** | `com.hellofig.FigApp` |
| **FIG Website** | https://hellofig.io/ |
| **Boilerplate Source** | ZyntroAI/fastapi-python-boilerplate |

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **FIG Detection** | `/api/fig/health` + `/api/fig/app` — FIG Agents ค้นพบได้ทันที |
| 🧠 **Knowledge Engine** | Index • Search • FS-Sync — RAG-ready |
| 🩹 **Self-Healing** | Diagnose • Auto-Fix • History — ตรวจ+ซ่อมอัตโนมัติ |
| 🔑 **Token Management** | Create • Rotate • Limit • Revoke — Auto-regenerate ก่อนหมดอายุ |
| 🛡️ **JWT Middleware** | Protect all endpoints • Scope-based permission • Daily rate-limit |
| 🐳 **Docker Compose** | Traefik • Services • Dev stack — one command |
| ☸️ **Kubernetes + Helm** | Production-ready deployment — `helm install fastapi-boilerplate ./helm` |
| 🧪 **CI/CD** | GitHub Actions • CodeQL • Pytest • Coverage — ทุก PR ตรวจสอบอัตโนมัติ |
| 💳 **Stripe Ready** | Payment flow integration — พร้อมขยาย |

---

## 🛠️ Tech Stack

 
 
Python 3.11+
├── FastAPI / Uvicorn
├── Pydantic v2
├── LangGraph (AI Agent)
├── PostgreSQL
├── Docker & Docker Compose
├── Traefik (Routing)
├── Helm + Kubernetes
├── Stripe SDK
└── FIG Agent Integration
 
plaintext
  

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/ZyntroAI/new-crystalcastle.git
cd new-crystalcastle
 
 
2. Create Virtual Environment
 
bash
  
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
 
 
3. Install Dependencies
 
bash
  
pip install -r requirements.txt
 
 
4. Configure Environment
 
bash
  
cp .env.example .env
 
 
แก้ไขค่าใน  .env  — ห้าม commit ค่า secret ขึ้น GitHub
 
Variable Description 
 DATABASE_URL  PostgreSQL connection 
 OPENAI_API_KEY  OpenAI inference key 
 STRIPE_SECRET_KEY  Stripe payments 
 APP_ENV   development  /  production  
 
5. Run Development Server
 
bash
  
uvicorn backend.main:app --reload
 
 
API พร้อมใช้งานที่:
 
- API:  http://127.0.0.1:8000 
- Swagger UI:  http://127.0.0.1:8000/docs 
- ReDoc:  http://127.0.0.1:8000/redoc 
 
🐳 Docker Compose (Alternative)
 
bash
  
docker compose up --build
 
 
 
 
🔐 FIG Endpoints — Agent Discovery
 
FIG Agents จะ detect ได้อัตโนมัติผ่าน 2 endpoints นี้:
 
 GET /api/fig/health 
 
json
  
{
  "name": "FIG ZyntroAI CrystalCastle",
  "version": "1.7.0-MERGED-FIG",
  "fig_commit": "4b0e59c7d34a7aa8053ad5286e1ee093fdb255f1",
  "fig_app": {
    "id": "com.hellofig.FigApp",
    "website": "https://hellofig.io/"
  },
  "hellofig": "https://hellofig.io/"
}
 
 
 GET /api/fig/app 
 
ข้อมูลแอปพลิเคชัน FIG — Play Store, Developer, Terms & Privacy
 
 
 
📁 Project Structure
 
plaintext
  
new-crystalcastle/
├── backend/
│   ├── main.py                  # Entry — FIG v1.7.0-MERGED-FIG
│   ├── middleware/
│   │   └── auth.py              # 🔐 JWT Scope-based Auth
│   └── routers/
│       ├── knowledge.py          # 🧠 Index • Search • Sync
│       ├── self_healing.py       # 🩹 Diagnose • Auto-Fix
│       └── token_management.py   # 🔑 Create • Rotate • Revoke
├── docs/
│   ├── FIG-INTEGRATION.md       # 📖 FIG Integration Full Docs
│   └── hero-fig.webp            # Phoenix + FastAPI Hero Banner
├── .github/workflows/           # CI/CD • CodeQL • Deployment
├── docker/                       # Dockerfile & configs
├── helm/                         # Kubernetes Helm Charts
├── tests/                        # Pytest Suite
├── .env.example                  # Environment Template
├── requirements.txt              # Minimal Dependencies
├── docker-compose.yml            # Local Dev Stack
└── README.md                     # ← This File
 
 
 
 
🔑 Authentication & Scopes
 
สร้างโทเคนผ่าน  /api/v1/tokens/create  พร้อมส่งใน Header:
 
http
  
Authorization: Bearer zntr_xxxxxxxxxxxxxxxxxxxx
 
 
Scope Permission 
 knowledge:read  ค้นหา/อ่านเอกสารความรู้ 
 knowledge:write  เพิ่ม/อัปเดตดัชนี 
 selfhealing:admin  ตรวจสภาพ & ซ่อมระบบ 
 tokens:read  ดูรายการโทเคน 
 tokens:admin  ยกเลิก/หมุนโทเคนทุกอัน 
 
 /api/v1/tokens/create  = สาธารณะ — ไม่ต้องส่งโทเคนก่อนสร้าง
 
 
 
🧪 Testing
 
bash
  
# Unit Tests
pytest tests/

# Coverage Report
pytest --cov=backend --cov-report=xml tests/

# Docker Stack Tests
docker compose exec backend pytest tests/integration
 
 
 
 
☸️ Kubernetes Deployment
 
bash
  
# Install
helm install crystalcastle ./helm

# Upgrade
helm upgrade crystalcastle ./helm

# Check Status
kubectl get pods -n crystalcastle
 
 
 
 
📝 Development Workflow
 
bash
  
git checkout -b feature/your-feature

git add .
git commit -m "feat: add feature description — #fig #chris"

git push -u origin feature/your-feature

gh pr create --base main --title "feat: your feature"
 
 
 
 
📋 Useful Commands
 
bash
  
# View Repo
gh repo view ZyntroAI/new-crystalcastle --web

# List Issues/PRs
gh issue list --repo ZyntroAI/new-crystalcastle
gh pr list --repo ZyntroAI/new-crystalcastle

# Workflows
gh workflow list --repo ZyntroAI/new-crystalcastle
 
 
 
 
⚠️ Notes from Boilerplate Merge
 
- ✅ แก้ไข  requirements.txt  — ลบเวอร์ชันที่ไม่มีจริง (P-014)
- ✅ ใช้ Safe Import Pattern — ป้องกัน ImportError (P-001, P-002, P-009)
- ✅ Minimal Dependencies — เฉพาะที่จำเป็นเท่านั้น
- ✅ FIG Commit:  4b0e59c  — ต้นทาง  ZyntroAI/fastapi-python-boilerplate 
 
 
 
📄 License
 
MIT License © 2026 ZyntroAI
 
 
 
💡 Next Steps:
 
- ตั้ง Cron Job — หมุนโทเคน + รัน Self-Healing อัตโนมัติ
- เชื่อมต่อ PostgreSQL — ย้าย In-Memory → DB ถาวร
- เพิ่ม Login/Password — ผสาน JWT แบบเต็มรูปแบบ
 
plaintext
  

---

## 📄 docs/FIG-INTEGRATION.md — เอกสาร FIG เฉพาะทาง

```markdown
---
title: FIG Integration Guide
aliases:
  - FIG Integration
  - HelloFig Integration
tags:
  - fig
  - hellofig
  - ai-agents
  - integration
  - zyntroai
created: 2026-09-29T20:00:00+07:00
version: 1.7.0-MERGED-FIG
---

# 🤝 FIG Integration — ZyntroAI CrystalCastle

> **FIG-V5.1-Balanced-Green-Biome-Solar-Dawn** · Detectable by FIG Agents · Native Protocol

---

## 🎯 Purpose

ทำให้ **FIG AI Agents** สามารถค้นพบ, ตรวจสอบ, และทำงานร่วมกับ **CrystalCastle** ได้ทันที โดยไม่ต้องกำหนดค่าเพิ่มเติม — ผ่าน Endpoint มาตรฐาน + ข้อมูลระบุตัวตนที่ชัดเจน

---

## 🆔 FIG Identity Schema

### Root Response — `/`
```json
{
  "name": "FIG ZyntroAI CrystalCastle",
  "version": "1.7.0-MERGED-FIG",
  "fig_commit": "4b0e59c7d34a7aa8053ad5286e1ee093fdb255f1",
  "fig_app": {
    "id": "com.hellofig.FigApp",
    "website": "https://hellofig.io/"
  },
  "hellofig": "https://hellofig.io/"
}
 
 
Health Check —  /api/fig/health 
 
สำหรับตรวจสอบสถานะ + ยืนยันความเข้ากันได้ของ FIG Protocol
 
Field Value Note 
 name  FIG ZyntroAI CrystalCastle ต้องขึ้นต้นด้วย  FIG   เพื่อให้ Agent ตรวจพบ 
 version   1.7.0-MERGED-FIG  แท็กเวอร์ชันมีคำว่า  -MERGED-FIG  
 fig_commit   4b0e59c...  Commit hash จาก fastapi-python-boilerplate 
 fig_app.id   com.hellofig.FigApp  — Play Store ID ✅ ตรงกับแอปจริง 
 fig_app.website   https://hellofig.io/  เว็บไซต์ทางการของ FIG 
 
App Info —  /api/fig/app 
 
ข้อมูลเพิ่มเติมเกี่ยวกับ FIG Application:
 
- ชื่อแอป: Fig - AI Agents & Automation
- นักพัฒนา: Fig Technology Inc.
- นโยบาย: Terms / Privacy — ลิงก์ตรงกับเว็บไซต์
 
 
 
🔍 How FIG Agents Detect
 
1️⃣ Header Scan
 
ค้นหาคำว่า  FIG  ใน:
 
- Title ของหน้าเอกสาร
-  name  ใน JSON response
- เวอร์ชันที่มี  -FIG 
 
2️⃣ Endpoint Probe
 
plaintext
  
GET / → ตรวจสอบรูปแบบมาตรฐาน
GET /api/fig/health → ยืนยันสถานะ
GET /api/fig/app → ดึงข้อมูลแอปพลิเคชัน
 
 
3️⃣ Verify Integrity
 
ตรงกับ  com.hellofig.FigApp  +  hellofig.io  → Trust Established ✅
 
 
 
🎨 Hero Banner
 
ภาพรวมระบบ —  docs/hero-fig.webp :
 
- บน: ฟีนิกซ์สีรุ้งบินเหนือหมู่บ้านพลังงานแสงอาทิตย์
- ล่าง: FastAPI Core Stack — Routes • Core • Config • Security • Logging • Services
- เชื่อมต่อ: ลำแสงข้อมูลจากหางนก → ชิปประมวลผล FastAPI
- แท็ก:  #fig #chris #zyntromedia #TeraAI 
 
 
 
🔄 Merge Context
 
Source
 
- Repository:  ZyntroAI/fastapi-python-boilerplate 
- Commit:  4b0e59c7d34a7aa8053ad5286e1ee093fdb255f1 
- Tag:  FIG-V5.1-Balanced-Green-Biome-Solar-Dawn 
 
Issues Resolved
 
ID Problem Resolution 
P-014  requirements.txt  pins versions ไม่มีจริง เหลือเฉพาะ dependency ที่จำเป็น 
P-001/P-002/P-009 ImportError บางสภาพการณ์ ใช้ Safe Import Pattern  try/except  
 
Files Changed
 
-  backend/main.py  — เพิ่ม FIG endpoints + VERSION
-  requirements.txt  — Minimal clean
-  docs/FIG-INTEGRATION.md  — เอกสารนี้
-  docs/hero-fig.webp  — ภาพประกอบ
 
 
 
🧩 Integration Points
 
System Status Note 
✅ FIG Detection Complete  /api/fig/*  + Root Response 
✅ JWT Auth Complete  middleware/auth.py  — Scope-based 
✅ Knowledge Engine Complete  /api/v1/knowledge/*  
✅ Self-Healing Complete  /api/v1/self-healing/*  
✅ Token Rotation Complete  /api/v1/tokens/*  — Auto-regen 
⏳ Cron Scheduler Pending ตั้งเวลา  rotate-all-expiring  +  heal  
⏳ Persistent DB Pending ย้ายจาก In-Memory → PostgreSQL 
 
 
 
🚀 Update Checklist
 
bash
  
# Push Branch
git checkout -b docs/zyntroai-fig-integration

cp main.py backend/main.py
cp docs/FIG-INTEGRATION.md docs/
cp hero-fig.webp docs/hero-fig.webp

git add backend/main.py docs/FIG-INTEGRATION.md docs/hero-fig.webp
git commit -m "feat: FIG integration — v1.7.0-MERGED-FIG"
git push origin docs/zyntroai-fig-integration

# Create PR
gh pr create --title "feat: FIG integration — detectable endpoints + identity" \
  --body "FIG-V5.1-Balanced-Green-Biome-Solar-Dawn merge complete"
 
 
 
 
📎 References
 
- 🔗 FIG Website: https://hellofig.io/
- 🔗 Play Store:  com.hellofig.FigApp 
- 🔗 Source Boilerplate: https://github.com/ZyntroAI/fastapi-python-boilerplate
- 🔗 CrystalCastle: https://github.com/ZyntroAI/new-crystalcastle
 
 
 
Generated: 2026-09-29 · Version:  1.7.0-MERGED-FIG 
 
plaintext
  

---

## ✅ สรุปสิ่งที่ส่งมอบ

| ไฟล์ | ตำแหน่ง | สถานะ |
|---|---|---|
| `README.md` | root/ | ✅ อัปเดตครบถ้วน — FIG Identity + Quick Start + Structure |
| `FIG-INTEGRATION.md` | `docs/` | ✅ เอกสารเฉพาะทาง — Detection Protocol + Merge Log |
| `hero-fig.webp` | `docs/` | ✅ ภาพประกอบ FIG Banner |
| `main.py` | `backend/` | ✅ FIG Endpoints + Version 1.7.0 |
| `requirements.txt` | root/ | ✅ Clean minimal — แก้ P-014 |

### 🔑 ความแตกต่างหลักจาก Boilerplate เดิม:
- เปลี่ยนชื่อ → **FIG ZyntroAI CrystalCastle**
- เพิ่ม **2 Endpoints FIG** สำหรับ Agent Detection
- ผสาน **Knowledge • Self-Healing • Token • JWT**
- แก้ไข Dependency → Minimal เท่านั้น
- จัดรูปแบบเอกสารเป็น **Obsidian Markdown** พร้อม Frontmatter

---

ต้องการให้สร้าง **Branch/PR ผ่าน GitHub CLI** ให้เลยไหมครับ? แค่บอก `push` ผมจัดให้ครับ 🚀

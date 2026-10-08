---
title: 🏗️ Infrastructure — MOC
aliases:
  - Infrastructure Index
  - IAC Map
  - DevOps Navigation
tags:
  - moc
  - infrastructure
  - devops
  - iac
  - zyntroai
  - type/moc
  - status/active
created: 2026-10-08
updated: 2026-10-08
status: active
owner: DevOps Team
review_cycle: 30d
version: 1.0
---

# 🏗️ Infrastructure — Map of Content

> [!moc] แผนผังระบบพื้นฐานทั้งหมด
> จุดรวมเอกสาร, มาตรฐาน, และการออกแบบ — ติดตามความครอบคลุมทุกส่วน

---

## 🧱 1. Core Standards & Policies

หลักการและกฎที่ทุกส่วนต้องปฏิบัติตาม

- [[กฎมาตรฐาน — Docker & Terraform]]
  - `Dockerfile` มาตรฐาน · Multi-stage · Security Hardening
  - `.dockerignore` · Image Size Optimization
  - Terraform Structure · State Management · Workspaces
- [[Infrastructure as Code — Policy]]
  - Branch Strategy · PR Requirements · Review Rules
  - Secret Management · No Hardcoding · `.gitignore` Standard
- [[Security Policy — Infrastructure]]
  - Least Privilege · Network Segmentation · Encryption Standards

---

## 🐳 2. Containerization — Docker

สร้าง จัดการ และปรับใช้คอนเทนเนอร์

- [[Dockerfile — Templates & Examples]]
  - Python/FastAPI · Node.js/Next.js · Multi-stage Builds
  - Non-root User · Healthcheck · Best Practice Checklist
- [[Docker Compose — Local Development]]
  - `docker-compose.yml` Template · Service Definition
  - Environment Overrides · Volume Mounts · Network
- [[Container Registry & Deployment]]
  - Build & Push Workflow · Semantic Tagging · Cleanup Policy

---

## 🏗️ 3. Infrastructure as Code — Terraform

จัดการทรัพยากรคลาวด์แบบโค้ด

- [[Terraform — Project Structure]]
  - `main.tf` · `variables.tf` · `outputs.tf` · `versions.tf`
  - Environment Separation: `dev/` `stg/` `prd/`
- [[Terraform — Backend & State]]
  - Remote State Storage · Locking · Encryption
  - `.gitignore` Rules · State Security
- [[Terraform — Providers & Modules]]
  - AWS · Docker · GitHub Provider Config
  - Reusable Modules · Version Pinning

---

## 🔄 4. CI/CD & Automation

ระบบรัน ตรวจสอบ และปรับใช้อัตโนมัติ

- [[GitHub Actions — Workflow Standards]]
  - `ci.yml` — Lint · Test · Security Scan
  - `deploy.yml` — Build · Push · Deploy
  - `branch-protection.yml` — Rules & Enforcement
- [[Pipeline — Quality Gates]]
  - Conventional Commits · CodeQL · Dependency Review
  - Required Checks · Merge Conditions
- [[Self-Hosted Runner — Setup]]
  - Registration · Permissions · Maintenance

---

## 🖥️ 5. Environments & Hosting

สภาพแวดล้อมและเป้าหมายปรับใช้

- [[Environment — dev]]
  - Purpose · Domain · Credentials · Access
- [[Environment — stg]]
  - Mirror of Production · Pre-release Validation
- [[Environment — prd]]
  - High Availability · Backup · Rollback Procedure
- [[Vercel — Frontend Deployment]]
  - Project Settings · Environment Variables · Custom Domain
- [[Cloud — Network & Security]]
  - Firewall Rules · Ingress · SSL/TLS · DNS

---

## 📊 6. Monitoring & Observability

เฝ้าดูสภาพระบบและแจ้งเตือน

- [[Logging — Standards]]
  - Structured Format · Retention · Levels
- [[Healthcheck — Endpoints]]
  - `/health` · `/ready` · `/live` Patterns
- [[Alerting — On-Call & Escalation]]
  - Critical Alerts · Notification Channels · Response Time

---

## 🛡️ 7. Security & Compliance

ความปลอดภัยระดับโครงสร้าง

- [[Secret Management — Overview]]
  - `.env.example` · GitHub Secrets · Environment Variables
  - Never Commit Secrets — Tools & Pre-commit Hooks
- [[Access Control — Infrastructure]]
  - IAM Roles · Service Accounts · Least Privilege
- [[Disaster Recovery — Plan]]
  - Backup Schedule · Recovery Time Objective · Restore Test

---

## 📋 8. Reference — Quick Links

### 🔧 Templates (คัดลอกใช้ได้)
- `Dockerfile.template` — [[Dockerfile — Production Template]]
- `docker-compose.yml` — [[Docker Compose — Base Template]]
- `versions.tf` — [[Terraform — Versions Template]]
- `ci.yml` — [[GitHub Actions — CI Template]]
- `deploy.yml` — [[GitHub Actions — Deploy Template]]
- `.gitignore` — [[Infrastructure — .gitignore Standard]]

### 📂 Repositories
- **new-crystalcastle** → https://github.com/ZyntroAI/new-crystalcastle
- **crystalcastleX** → https://github.com/zyntromedia/crystalcastleX
- **ZyntroAI-Project** → https://github.com/zyntromedia/ZyntroAI-Project

### 📌 External Docs
- [Docker Docs](https://docs.docker.com)
- [Terraform Docs](https://developer.hashicorp.com/terraform)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## ✅ Status Board

| ส่วน | ความคืบหน้า | สถานะ |
|---|---|---|
| Core Standards | ✅ เสร็จ | 100% |
| Docker Templates | ✅ เสร็จ | 100% |
| Terraform Structure | ⚙️ กำลังทำ | 60% |
| CI/CD Workflows | ⚙️ กำลังทำ | 80% |
| Environment Docs | ⏳ รอเริ่ม | 0% |
| Monitoring | ⏳ รอเริ่ม | 0% |
| Security & Secrets | ⚙️ กำลังทำ | 40% |

---

## 🗺️ ทางลัด MOC อื่นๆ

- [[🏠 Home — ZyntroAI]]
- [[🧠 AI & Agents — MOC]]
- [[📦 Projects — MOC]]
- [[👥 Team & Roles — MOC]]

---

## 📝 บันทึกการเปลี่ยนแปลง
- `2026-10-08` — สร้างฉบับแรก: 8 ส่วนหลัก + Status Board + ทางลัด

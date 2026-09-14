ต่อไปนี้คือส่วน **README.md Update (GitHub Actions & Branch Strategy for Origin)** ที่เขียนให้เข้ากับเอกสาร README ปัจจุบันของโปรเจกต์ และสอดคล้องกับ Organization **ZyntroAI** และ FIG v4 Enterprise

---

# CI/CD Workflows & Origin Branch Strategy

## Branch Model

The repository uses **Origin** as the primary integration branch.

```text
Origin (default)
│
├── feature/*
├── fix/*
├── hotfix/*
├── release/*
└── experimental/*
```

All pull requests should target **Origin**.

Protected branches:

```text
Origin
main
production
```

Branch protection rules:

- Require Pull Request
- Require Status Checks
- Require Code Owner Review
- Require Signed Commits
- Require Conversation Resolution
- Require 2 Reviews for MasterFiles changes

---

## GitHub Actions Structure

Workflows are organized by responsibility.

```text
.github/
└── workflows/
    ├── ci.yml
    ├── cd-deploy.yml
    ├── scheduled-cleanup.yml
    ├── release.yml
    ├── notify.yml
    ├── dependabot-auto-merge.yml
    ├── security-scan.yml
    ├── codeql.yml
    ├── container-scan.yml
    └── masterfiles-guard.yml
```

---

## CI Workflow

**Purpose**

- Lint
- Formatting Validation
- Unit Tests
- Integration Tests
- Coverage
- Docker Build Verification

Trigger:

```yaml
on:
  push:
    branches:
      - Origin

  pull_request:
    branches:
      - Origin
```

Pipeline:

```text
Checkout
 ↓
Install
 ↓
Lint
 ↓
Format Check
 ↓
Tests
 ↓
Coverage
 ↓
Build
 ↓
Artifact Upload
```

---

## CD Workflow

Deployment is executed only after CI passes.

Flow:

```text
Origin
 ↓
Deploy Staging
 ↓
Smoke Test
 ↓
Manual Approval
 ↓
Deploy Production
```

Environments:

| Environment | Purpose |
|------------|----------|
| staging | Validation |
| production | Live Traffic |

---

## Scheduled Operations

Scheduled maintenance tasks run automatically.

Examples:

```text
- Database Backup
- Cache Cleanup
- Docker Cleanup
- Metrics Archive
- Security Audit
```

Schedule:

```yaml
cron: "0 0 * * 1"
```

Every Monday at 00:00 UTC.

---

## Release Management

A release is created when a version tag is pushed.

```text
v1.0.0
v1.1.0
v2.0.0
```

Release workflow:

```text
Build
 ↓
Security Scan
 ↓
Publish Docker Image
 ↓
Create GitHub Release
 ↓
Generate Release Notes
```

---

## Notifications

Notifications are sent for:

- CI Failed
- CI Success
- Production Deploy
- Security Incident
- Release Published

Supported channels:

```text
Slack
Email
Microsoft Teams
Webhook
```

---

## Security Workflows

The repository implements security controls through dedicated workflows.

### Secret Scan

Checks:

```text
API Keys
JWT Secrets
Cloud Credentials
Database Passwords
Private Keys
```

---

### CodeQL

Static analysis:

```text
Python
JavaScript
TypeScript
Docker
GitHub Actions
```

---

### Container Scan

Scans:

```text
Docker Images
Base Images
Package Vulnerabilities
OS Vulnerabilities
```

Tools:

```text
Trivy
Grype
Docker Scout
```

---

## MasterFiles Protection

MasterFiles are considered critical assets.

Protected paths:

```text
masterfiles/
config/
system/
settings/
.github/
```

Rules:

```text
Owner Review Required
2 Approvals Required
No Direct Push
No Force Push
Audit Log Enabled
```

Workflow:

```yaml
masterfiles-guard.yml
```

Validation:

```text
READ
WRITE
UPDATE
DELETE
```

Permissions are enforced through FIG RBAC.

---

## Organization Governance

Organization:

```text
ZyntroAI
```

Requirements:

```text
2FA Required
Owner Governance
Audit Logging
Security Reviews
Protected Secrets
```

Sensitive values must never be stored in source code.

Store secrets in:

```text
Settings
 └── Secrets and Variables
      └── Actions
```

Examples:

```text
VERCEL_TOKEN
DOCKER_PASSWORD
CODECOV_TOKEN
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
JWT_SECRET
MASTERFILES_TOKEN
SLACK_WEBHOOK
```

---

## Enterprise Recommendations

Recommended additions:

- Full SHA Pinning for all GitHub Actions
- Environment Protection Rules
- Dependabot Auto Merge
- SBOM Generation
- SLSA Build Provenance
- Artifact Signing
- OIDC Cloud Authentication
- Trivy Security Scanning
- CodeQL Advanced Security
- MasterFiles Approval Gate

---

## Deployment Flow

```text
Developer
    ↓
Pull Request
    ↓
CI Pipeline
    ↓
Security Scans
    ↓
Review Approval
    ↓
Merge → Origin
    ↓
Deploy Staging
    ↓
Validation
    ↓
Production Approval
    ↓
Deploy Production
    ↓
Notification
```

---

## FIG v4 Enterprise Integration

FIG integrates directly with repository governance:

```text
FIG API Gateway
 + CI/CD
 + RBAC
 + MasterFiles Engine
 + Audit Logging
 + Security Layer
 + Organization Governance
```

This ensures all API operations, deployments, security checks, and MasterFiles updates remain compliant with the ZyntroAI Enterprise workflow model.

-----------

******WAIT MERGE TO Lasted******

Here’s **การออกแบบ GitHub Actions Workflows สำหรับ `Origin`** (หลังจากเปลี่ยนเป็น default branch แล้ว) ที่แยก **CI** และ **Workflows อื่นๆ** อย่างชัดเจน พร้อมคำแนะนำสำหรับ FastAPI project ของคุณ:

---

---

## 📁 **โครงสร้างไฟล์ Workflows**
```
.github/
└── workflows/
    ├── ci.yml                # CI (Test, Lint, Build)
    ├── cd-deploy.yml         # CD (Deploy to Staging/Production)
    ├── scheduled-cleanup.yml # Scheduled Jobs
    ├── release.yml           # Release Management
    └── notify.yml            # Notifications (Slack/Email)
```

---

---

## 🔧 **1. CI Workflow (`ci.yml`)**
**หน้าที่:** รัน **Test, Lint, Build** ทุกครั้งที่มี `push` หรือ `pull_request` ไปยัง `Origin` หรือ branch อื่นๆ

```yaml
# .github/workflows/ci.yml
name: CI - Test & Lint

on:
  push:
    branches: [ Origin, main ]  # รันทั้ง Origin และ main (ถ้ายังใช้ main ร่วมด้วย)
  pull_request:
    branches: [ Origin ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]  # ตัวอย่างสำหรับ Python

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8 black

      - name: Run Lint (Flake8)
        run: flake8 .

      - name: Run Formatter (Black)
        run: black --check .

      - name: Run Tests with Coverage
        run: |
          pytest --cov=./ --cov-report=xml
          # Upload coverage to Codecov (ถ้าต้องการ)
          curl -Os https://uploader.codecov.io/latest/linux/codecov
          chmod +x codecov
          ./codecov -t ${{ secrets.CODECOV_TOKEN }}

  build:
    needs: test  # รอให้ test เสร็จก่อน
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker Image (ตัวอย่าง)
        run: |
          docker build -t zyntroai/fastapi-project:latest .
          docker images
```

---

---

## 🚀 **2. CD Workflow (`cd-deploy.yml`)**
**หน้าที่:** Deploy โค้ดไปยัง **Staging** และ **Production** หลังจาก CI ผ่าน

```yaml
# .github/workflows/cd-deploy.yml
name: CD - Deploy

on:
  push:
    branches: [ Origin ]  # Deploy เฉพาะเมื่อ push ไปยัง Origin
  workflow_dispatch:      # หรือกด manual deploy ใน GitHub UI

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.zyntroai.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Staging (Vercel)
        run: |
          vercel --token ${{ secrets.VERCEL_TOKEN }} --env staging
        env:
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}

  deploy-production:
    needs: deploy-staging  # รอ staging deploy เสร็จก่อน
    if: github.ref == 'refs/heads/Origin'  # Deploy เฉพาะเมื่อ push ไป Origin
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://api.zyntroai.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Production (Vercel)
        run: |
          vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
```

---

---

## ⏰ **3. Scheduled Workflow (`scheduled-cleanup.yml`)**
**หน้าที่:** รันงานบำรุงรักษา (เช่น ลบ cache, backup database) ตามกำหนดการ

```yaml
# .github/workflows/scheduled-cleanup.yml
name: Scheduled - Cleanup & Backup

on:
  schedule:
    - cron: '0 0 * * 1'  # รันทุกวันจันทร์ เวลา 00:00 UTC (07:00 ICT)
  workflow_dispatch:      # หรือกด manual ใน GitHub UI

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Clean old Docker images
        run: |
          docker system prune -af

  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Backup Database
        run: |
          pg_dump -U ${{ secrets.DB_USER }} -h ${{ secrets.DB_HOST }} ${{ secrets.DB_NAME }} > backup.sql
          # Upload backup ไปยัง S3/Google Drive (ตัวอย่าง)
          aws s3 cp backup.sql s3://zyntroai-backups/backup-$(date +%Y%m%d).sql
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

---

## 📦 **4. Release Workflow (`release.yml`)**
**หน้าที่:** สร้าง **Release** และ Publish Package (เช่น Docker Image, PyPI) เมื่อมี tag ใหม่

```yaml
# .github/workflows/release.yml
name: Release - Publish

on:
  push:
    tags:
      - 'v*'  # Trigger เมื่อ push tag เช่น v1.0.0

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker Image
        run: |
          docker build -t zyntroai/fastapi-project:${{ github.ref_name }} .
          docker tag zyntroai/fastapi-project:${{ github.ref_name }} zyntroai/fastapi-project:latest

      - name: Login to Docker Hub
        run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin

      - name: Push Docker Image
        run: |
          docker push zyntroai/fastapi-project:${{ github.ref_name }}
          docker push zyntroai/fastapi-project:latest

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: ${{ github.ref_name }}
          name: Release ${{ github.ref_name }}
          body: |
            Changes in this release:
            - Fix bug in API endpoint
            - Update dependencies
```

---

---

## 📢 **5. Notification Workflow (`notify.yml`)**
**หน้าที่:** ส่งแจ้งเตือนไปยัง **Slack** หรือ **Email** เมื่อ CI/CD สำเร็จ/ล้มเหลว

```yaml
# .github/workflows/notify.yml
name: Notify - Slack Alerts

on:
  workflow_run:
    workflows: ["CI - Test & Lint", "CD - Deploy"]  # รันหลัง CI/CD
    types:
      - completed

jobs:
  notify:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion != 'neutral' }}
    steps:
      - name: Send Slack Notification
        uses: rtCamp/action-slack-notify@v2
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
          SLACK_COLOR: ${{ github.event.workflow_run.conclusion == 'success' && 'good' || 'danger' }}
          SLACK_TITLE: "Workflow ${{ github.event.workflow_run.conclusion }}"
          SLACK_MESSAGE: |
            Workflow *${{ github.event.workflow_run.name }}* ${{ github.event.workflow_run.conclusion == 'success' && '✅ Success' || '❌ Failed' }}
            Commit: ${{ github.event.workflow_run.head_commit.message }}
            Branch: ${{ github.event.workflow_run.head_branch }}
            Link: ${{ github.event.workflow_run.html_url }}
```

---

---

## 🔐 **Secrets ที่จำเป็น**
ไปที่ **Settings > Secrets > Actions** เพื่อเพิ่ม:
| **Secret Name**          | **คำอธิบาย**                          |
|--------------------------|----------------------------------------|
| `VERCEL_TOKEN`           | Token สำหรับ Vercel Deployment         |
| `VERCEL_PROJECT_ID`      | Project ID ใน Vercel                   |
| `VERCEL_ORG_ID`          | Organization ID ใน Vercel              |
| `DOCKER_USERNAME`        | Username Docker Hub                     |
| `DOCKER_PASSWORD`        | Password Docker Hub                    |
| `CODECOV_TOKEN`          | Token สำหรับ Codecov (ถ้าใช้)          |
| `SLACK_WEBHOOK`         | Slack Incoming Webhook URL             |
| `AWS_ACCESS_KEY_ID`      | AWS Key สำหรับ Backup                  |
| `AWS_SECRET_ACCESS_KEY`  | AWS Secret Key                         |
| `DB_USER`, `DB_HOST`, `DB_NAME` | ข้อมูล database สำหรับ Backup |

---

---

## 📌 **คำแนะนำเพิ่มเติม**
1. **Environment Protection**
   - ใน `cd-deploy.yml` ใช้ `environment:` เพื่อกำหนด **approval** ก่อน deploy production:
     ```yaml
     environment:
       name: production
       url: https://api.zyntroai.com
     ```
     (GitHub จะขอ approval ก่อนรัน job นี้)

2. **Matrix Testing**
   - ใน `ci.yml` ใช้ `matrix` เพื่อทดสอบกับ **Python version หลายๆ เวอร์ชัน** หรือ **OS หลายๆ ตัว**

3. **Artifacts**
   - ถ้าต้องการเก็บผลลัพธ์จาก CI (เช่น test report, coverage):
     ```yaml
     - name: Upload Test Report
       uses: actions/upload-artifact@v4
       with:
         name: pytest-report
         path: test-results/
     ```

4. **Cache Dependencies**
   - เพิ่ม cache สำหรับ `pip` เพื่อเร่งความเร็ว:
     ```yaml
     - name: Cache pip
       uses: actions/cache@v3
       with:
         path: ~/.cache/pip
         key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
     ```

5. **Auto-merge Dependabot**
   - สร้าง workflow สำหรับ auto-merge Dependabot PR ถ้า CI ผ่าน:
     ```yaml
     # .github/workflows/dependabot-auto-merge.yml
     name: Dependabot Auto Merge
     on:
       pull_request:
         branches: [ Origin ]
     jobs:
       auto-merge:
         if: github.actor == 'dependabot[bot]'
         runs-on: ubuntu-latest
         steps:
           - uses: actions/github-script@v7
             with:
               script: |
                 github.pulls.merge({
                   owner: context.repo.owner,
                   repo: context.repo.repo,
                   pull_number: context.issue.number,
                   merge_method: 'squash'
                 })
     ```

---

---
## ✅ **สรุปการทำงาน**
1. **Developer push code → `Origin`**
   → **CI Workflow** รัน (Test, Lint, Build)
   → ถ้า **CI ผ่าน** → **CD Workflow** รัน (Deploy to Staging)
   → ถ้า **Staging OK** → **CD Workflow** Deploy to Production (หรือรอ approval)
2. **ทุกวันจันทร์** → **Scheduled Workflow** รัน (Cleanup, Backup)
3. **เมื่อมี tag ใหม่** → **Release Workflow** รัน (Publish Docker Image, Create Release)
4. **หลัง CI/CD เสร็จ** → **Notification Workflow** ส่งแจ้งเตือนไปยัง Slack

---
**✨ พร้อมใช้งาน!**
คุณสามารถ copy code นี้ไปวางใน `.github/workflows/` ของ repo ได้เลย ครับ
ถ้าต้องการปรับแต่ง (เช่น ใช้ AWS ECS แทน Vercel) ให้บอกมาได้นะ!| `app/core/main.py` | A second, fuller FastAPI app (items/users routers, DB session, origin middleware) |
| `graphql_api/` | Standalone GraphQL service — Strawberry + async SQLAlchemy + JWT + Alembic, own `requirements.txt`, `docker-compose.yml`, tests |
| `frontend/` | React 18 + Vite 8 + TypeScript frontend (own `package.json`, `Dockerfile`, `tsconfig.json`) |
| `skills/` | Reusable AI-agent skill definitions (`fetching`, `changelog-auto-update`, `credential-management`, `patch`, `research`, …) |
| `deliverables/` | 21 self-contained feature suites, each with its own README and tests — see [`deliverables/README.md`](./deliverables/README.md) |
| `docs/` | Reference library (30 files): GraphQL, FireCrawl, Google Chat, GitHub Actions, MCP, incident drills |
| `tests/` | Test suite — `unit/`, `e2e/`, plus repo-level tests (`tests/conftest.py`, `pytest.ini` at root) |
| `helm/`, `k8s/` | Deployment — Helm chart (`oauth-app`) and Kubernetes manifests (deployment, HPA, ingress, monitoring) |
| `.github/workflows/` | 13 workflow files — CI/CD, release drafter, secret scan, coverage, auto-index |
| `docker-compose.yml` | Local platform stack: Postgres 16, Redis 7, MinIO, Gitea, Prometheus, Grafana, Traefik, stripe-mock |

---

## Quick start

### 1. The OAuth2 API

```bash
cp .env.example .env        # then fill in the values (see Configuration)
pip install -r requirements.txt
uvicorn main:app --reload
```

- Swagger UI — `http://localhost:8000/docs`
- Health — `http://localhost:8000/health`
- Root — `http://localhost:8000/`

### 2. The local platform stack

```bash
docker compose up -d
```

Brings up Postgres, Redis, MinIO, Gitea, Prometheus, Grafana, Traefik and a Stripe
mock — the backing services the suites and integration examples expect.

### 3. The React frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. A deliverable suite

Every suite under `deliverables/` is self-contained. Several ship their own
`docker-compose.yml` plus a seed script, so a fresh clone is one command from a
running stack — for example `deliverables/product-crud/`.

---

## Entrypoints — there are three

The repository contains three separate `app = FastAPI(...)` definitions. Which one
you run depends on what you want:

| Module | Run with | What it is |
| ------ | -------- | ---------- |
| `main.py` | `uvicorn main:app` | The documented OAuth2 PKCE API. Routers: `/auth`, `/auth/callback`, `/health`. |
| `app/main.py` | `uvicorn app.main:app` | Identical to `main.py` (same content, different import path). |
| `app/core/main.py` | `uvicorn app.core.main:app` | The fuller application: items/users routers, DB init/close lifespan, origin validation, gzip, OpenAPI customisation. |

`main.py` and `app/main.py` are duplicates of each other — pick one. `app/core/main.py`
is a different, more complete application and is the more likely base for real work.
This duplication is a known cleanup item, not an intentional layering.

---

## Configuration

`.env.example` is the template. The settings class is `app/core/config.py` (Pydantic
Settings), and it reads the same `.env`.

**Required:**

| Variable | Notes |
| -------- | ----- |
| `OAUTH_CLIENT_ID` | No default — the app will not start without it |
| `OAUTH_CLIENT_SECRET` | Optional; PKCE does not need a client secret |

**Common:**

| Variable | Default | Notes |
| -------- | ------- | ----- |
| `ENV` | `local` | `local` \| `vercel` \| `production` — selects callback URL, frontend URL, and whether `/docs` is exposed |
| `JWT_SECRET` | placeholder | **Change in production** |
| `JWT_ALGORITHM` / `JWT_EXPIRE_MINUTES` | `HS256` / `60` | |
| `REDIS_URL` | unset | Optional — token storage |
| `CREDENTIAL_BROKER_URL` / `BROKER_TOKEN` | unset | Central credential broker (metadata only; no raw secrets) |

Callback and frontend URLs are derived from `ENV` — see `OAUTH_CALLBACK_URL` and
`FRONTEND_URL` in `app/core/config.py`.

> **Known state — `.env` is tracked in git.** Despite `.gitignore` listing `.env`, the
> file is committed and carries real keys (BytePlus credentials and WhatsApp Cloud API
> tokens). Treat it as compromised: move those values into CI secrets, rotate them, and
> `git rm --cached .env`. The tracked file is also incomplete relative to the settings
> class — it has no `OAUTH_CLIENT_ID`, so a fresh clone cannot start the API as-is.

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

`pytest.ini` sets `asyncio_mode = auto`. `requirements-dev.txt` layers pytest,
pytest-asyncio, pytest-cov and httpx on top of the runtime requirements, plus the
repo's lint toolchain (ruff, black, isort, mypy).

Tests live in `tests/` (`unit/`, `e2e/`, and repo-level files) and inside individual
deliverable suites. Run a suite's own tests from its directory.

> **Known state — the root suite does not collect.** `app/core/config.py` declares
> `OAUTH_CLIENT_ID: str` as a required field, and no environment block supplies it, so
> collection fails before any test runs. Set `OAUTH_CLIENT_ID` (any non-empty value) in
> the environment to collect. Some root test files also use hyphenated names
> (`test-escalation.py`), which pytest cannot import as modules; those were written as
> runnable scripts.

---

## Deliverables

`deliverables/` holds 21 self-contained suites. Each is a complete piece of work —
code, tests, and its own README — rather than a fragment of the main app:

`agent-core` · `agent-security-suite` · `agent-skill-template` · `ai-agent-skills` ·
`ai-agents-decision-pack` · `ai-gateway-architecture-review` · `azure-cli-2026` ·
`cwe1321-protection-suite` · `fastapi-obsidian-backend` · `firecrawl-fastapi` ·
`gemini-cli-skills` · `gh-devops-toolkit` · `manus-client` · `notebooklm-access-suite` ·
`notebooklm-link-share` · `onspace-ai` · `onspace-platform-integration` · `pm-backend` ·
`product-crud` · `pure-agent-dev`

See [`deliverables/README.md`](./deliverables/README.md) for one-line descriptions and
links into each suite.

---

## Documentation

[`docs/README.md`](./docs/README.md) is the index. Highlights:

- **MCP** — [`docs/MCP-Guide-Complete.md`](./docs/MCP-Guide-Complete.md), a troubleshooting guide, plus `scripts/check-mcp-environment.sh` (checks Google Cloud ADC, runtimes, and API keys; never prints secret values)
- **Security** — [`docs/knowledge-ai-agent-security-devsecops-2026.md`](./docs/knowledge-ai-agent-security-devsecops-2026.md): sandbox design, trust tiers, state isolation
- **GitHub / DevOps** — [`docs/github-cli-gh-reference.md`](./docs/github-cli-gh-reference.md), [`docs/research-tools-free-guide.md`](./docs/research-tools-free-guide.md), `docs/github-actions/`
- **Integrations** — `docs/GraphQL/`, `docs/FireCrawl_REST_API/`, `docs/GoogleChat_REST_API/`, `docs/supabase.md`

Also at the root: [`ROADMAP.md`](./ROADMAP.md) (8-phase plan and milestone M4),
[`TASKS.md`](./TASKS.md), [`CHANGELOG.md`](./CHANGELOG.md),
[`PROBLEMS.md`](./PROBLEMS.md) for open blockers,
[`SECURITY.md`](./SECURITY.md), [`CONTRIBUTING.md`](./CONTRIBUTING.md),
[`RELEASE.md`](./RELEASE.md).

---

## CI/CD & supply-chain integrity

The repository's policy is **full-SHA pinning**: every `uses:` reference should point at
a 40-character commit SHA, never a mutable tag such as `@v4`.

**Known state (verified 2026-09-13 against `main`):**

- Of the `uses:` references in `.github/workflows/`, **20 are SHA-pinned and 61 still
  use tags** (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`,
  `github/codeql-action/*@v3`, and others). `ci.yml` itself is correctly pinned.
- **Five workflow files are not valid YAML as committed, so they never run:**

  | File | Parse error |
  | ---- | ----------- |
  | `.github/workflows/Auto-Index-Sync.yml` | invalid simple key |
  | `.github/workflows/dependabot-automerge.yml` | invalid simple key |
  | `.github/workflows/secret-scan.yml` | invalid simple key |
  | `.github/workflows/test-suite.yml` | more than one document in the stream |
  | `.github/workflows/github-actions-autodebug-autorerun` | mapping values not allowed (and it has no `.yml`/`.yaml` extension, so Actions ignores it regardless) |

- Because several jobs cannot start, a feature PR can show red checks even when its own
  tests pass locally. Background and the repair history are in
  [`CHANGELOG.md`](./CHANGELOG.md) and [`PROBLEMS.md`](./PROBLEMS.md).

Fixing workflows needs write access to `.github/workflows/`, which the automation App
does not hold by default — it must be applied by a maintainer or with elevated App
permissions. See [`SECURITY.md`](./SECURITY.md) for the policy.

---

## Repository hygiene — known state

- **The root carries 212 entries.** Loose scripts, dashboard exports, notebook HTML,
  archives, and chat exports sit alongside the real tree. It has not been pruned or
  classified. Expect to have to look around.
- **The root Node tooling is declared but not wired up.** `package.json` lists `vercel`,
  `eslint`, `prettier`, `vitest` and `semantic-release`, but there is **no ESLint config**
  at the root (so `npm run lint` fails), **no `.releaserc`** for semantic-release, and
  **`scripts.vite` holds a version range (`">=6.4.3"`) where a command belongs.**
  `package-lock.json` exists but should be regenerated before trusting it. Treat the root
  Node path as present but unverified.
- **The root `Dockerfile` does not build the Python API.** It is a Node multi-stage build
  (`node:26-alpine`, `EXPOSE 4000`, `CMD ["node", "dist/index.js"]`). The Python app has
  its own `app/Dockerfile`, and `Dockerfile.txt` is a quoted Dockerfile stored as text
  (with an Alpine/pgloader importer stage and a uv-based Python agent stage) rather than
  a usable file.
- **`uvicorn main:app --reload` starts the OAuth API, not the main application.**
  See [Entrypoints](#entrypoints--there-are-three).

---

## License

MIT — see [LICENSE](./LICENSE).

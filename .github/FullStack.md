🚀 FullStack Development & DevOps Skillsbook — Optimized Edition
 
A comprehensive, production-ready guide covering full-stack development, DevOps workflows, Docker, Kubernetes, CI/CD, and AI integration.
 
 
 
📋 Table of Contents
 
- 🎯 Executive Overview
- 🔄 Complete Workflow Pipeline
- 📁 Repository Structure
- 📋 Project Planning
- 💻 Feature Development
- 🔨 Build & Testing
- 📚 Documentation
- 🐳 Docker & Containerization
- ⚙️ CI/CD with GitHub Actions
- ☸️ Kubernetes Deployment
- 🧪 UAT Environment
- 🤖 AI Integration (Vertex MCP)
- 🔒 Security & Compliance
- 🔧 Maintenance & Automation
- 📊 Quick Reference
- ✅ Pre-Deployment Checklist
 
 
 
🎯 Executive Overview
 
Phase Command Objective Output 
Plan  /create-plans  Define scope, architecture, risks Spec + Tech Design 
Develop  /feat  Implement features in isolation PR ready for review 
Verify  /build  +  /test  Validate correctness & quality Passing artifacts 
Document  /docs  Keep docs in sync with code Updated docs 
Package  /docker-compose  Containerize consistently Multi-service stack 
Validate  /github-actions  Enforce quality gates Green CI pipeline 
Deploy  /deploy dev → /deploy uat → /deploy prod  Phased rollout with approvals Production release 
Intelligence  /vertex-mcp  Integrate AI capabilities AI-augmented workflows 
Maintain  /chores  +  /summaries  Keep system healthy Audit + status report 
 
 
 
🔄 Complete Workflow Pipeline
 
plaintext
  
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  PLANNING   │ →  │  DEVELOPMENT  │ →  │   VERIFICATION  │
│ /create-plans │   │   /feat      │    │ /build /test  │
└─────────────┘    └──────────────┘    └──────┬───────┘
                                                │
┌─────────────┐    ┌──────────────┐    ┌──────▼───────┐
│  PROD READY │ ←  │   UAT PASS   │ ←  │  DEPLOY DEV  │
│ /deploy prod│    │ /deploy uat │    │ /github-actions│
└──────┬──────┘    └──────────────┘    └──────────────┘
       │
┌──────▼───────┐    ┌──────────────┐    ┌──────────────┐
│  MONITORING  │ ← │ MAINTENANCE  │ ←  │  AI ENRICH   │
│ /summaries   │    │   /chores   │    │ /vertex-mcp │
└──────────────┘    └──────────────┘    └──────────────┘
 
 
 
 
📁 Repository Structure — Optimized
 
plaintext
  
.
├── .github/workflows/       # CI/CD pipelines
│   ├── ci.yml              # Build + test + lint
│   ├── secret-scan.yml     # Secrets detection
│   ├── dependency-review.yml # Vulnerability scan
│   ├── deploy-dev.yml      # Auto deploy dev
│   ├── deploy-uat.yml      # Manual deploy UAT
│   └── release.yml         # Tag → deploy prod
├── backend/                # API / services
├── frontend/               # UI / client
├── docker/                 # Dockerfiles & configs
│   ├── Dockerfile.dev
│   └── Dockerfile.prod
├── k8s/                    # Kubernetes manifests
│   ├── base/               # Base resources
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── kustomization.yaml
│   └── overlays/           # Env-specific configs
│       ├── dev/kustomization.yaml
│       ├── uat/kustomization.yaml
│       └── prod/kustomization.yaml
├── helm/app/               # Helm charts
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-uat.yaml
│   └── templates/
├── scripts/                # Utility scripts
│   ├── backup.sh
│   ├── health-check.sh
│   ├── deploy.sh
│   └── maintenance.sh
├── docs/                   # Project documentation
│   ├── architecture.md
│   ├── api.md
│   ├── development.md
│   ├── deployment.md
│   ├── security.md
│   ├── troubleshooting.md
│   └── runbook.md
├── .github/ISSUE_TEMPLATE/ # Standardized issue templates
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── docker-compose.dev.yml
├── Makefile
├── README.md
└── .env.example            # Template — NEVER commit .env
 
 
 
 
📋 Project Planning
 
Planning Checklist
 
Requirements — Functional, non-functional, constraints
Architecture — System design, tech stack, data flows
Security — Auth model, data classification, network boundaries
Environments — Dev / UAT / Prod strategy, isolation rules
Risks — Dependencies, external APIs, compliance requirements
Timeline — Milestones, deliverables, dependencies
 
 
 
💻 Feature Development
 
Standard Git Workflow
 
bash
  
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feat/short-description

# Work + commit frequently
git add .
git commit -m "feat: implement user authentication"

# Keep branch updated
git pull origin main --rebase

# Push and open PR
git push -u origin feat/short-description
# Create PR → Request review → Merge when approved
 
 
Branch Naming Convention
 
Prefix Purpose Example 
 feat/  New feature  feat/user-login  
 fix/  Bug fix  fix/login-timeout  
 docs/  Documentation  docs/api-endpoints  
 refactor/  Code refactoring  refactor/auth-service  
 chore/  Maintenance  chore/update-deps  
 
 
 
🔨 Build & Testing
 
Makefile Standard Targets
 
makefile
  
.PHONY: all setup build lint test clean help

all: setup lint test build

setup:  ## Install dependencies
	@echo "🔧 Setting up project..."

build:  ## Build application
	@echo "🏗️ Building..."

lint:   ## Run linters
	@echo "🔍 Linting..."

test:   ## Run unit tests
	@echo "🧪 Running tests..."

test-integration:  ## Run integration tests
	@echo "🔗 Running integration tests..."

test-e2e:  ## Run end-to-end tests
	@echo "🎭 Running E2E tests..."

clean:  ## Clean build artifacts
	@echo "🧹 Cleaning..."

help:   ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
 
 
Test Pyramid — Recommended Balance
 
plaintext
  
        /\
       /E2E\        ← Few (Critical paths only)
      /------\
     /Integration\   ← Moderate (API/Service contracts)
    /----------\
   /   Unit     \    ← Most (Fast, isolated logic)
  /==============\
 
 
 
 
📚 Documentation
 
Docs-as-Code Principles
 
- ✅ Close to code — Store docs in repo, not separate wiki
- ✅ Versioned together — Same commit as code changes
- ✅ Reviewable — PR includes doc changes
- ✅ Generated where possible — API docs from OpenAPI/Swagger
 
Minimum Documentation Set
 
Document Purpose Owner 
 README.md  Quickstart, overview All devs 
 architecture.md  System design, diagrams, decisions Tech Lead 
 api.md  Endpoints, request/response examples Backend Team 
 development.md  Local setup, common commands All devs 
 deployment.md  Env guide, promote procedures DevOps 
 troubleshooting.md  Known issues + fixes Everyone contributes 
 
 
 
🐳 Docker & Containerization
 
Multi-Stage Build Example
 
dockerfile
  
# ---- Builder Stage ----
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Production Stage ----
FROM node:22-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
 
 
Docker Compose — Local Development
 
yaml
  
version: '3.8'

x-common-env: &common-env
  NODE_ENV: development
  LOG_LEVEL: debug

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports: ["8080:8080"]
    environment:
      <<: *common-env
      DB_HOST: db
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - /app/node_modules
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports: ["3000:3000"]
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - api

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devuser"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
 
 
 
 
⚙️ CI/CD with GitHub Actions
 
Pipeline Design Strategy
 
plaintext
  
Pull Request → CI (Build + Test + Lint) → Merge to Main
     ↓
   Main Branch → CI Passes → Auto Deploy DEV → Notify Team
     ↓
   Tag Release Candidate → Manual Approval → Deploy UAT → Test → Approve → Deploy PROD
 
 
CI Pipeline Template ( ci.yml )
 
yaml
  
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel old runs on new pushes

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm test -- --coverage

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: my-app:ci
          cache-from: type=gha
          cache-to: type=gha,mode=max

  scan:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'my-app:ci'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
 
 
Deployment Promotion Flow
 
plaintext
  
main branch ──► DEV (Auto)
     │
     ├─── Tag: v1.2.3-rc1 ──► UAT (Manual trigger)
     │                              │
     │                              ▼
     │                         ✅ UAT Approved?
     │                              │
     └─── Tag: v1.2.3 ─────────────► PROD (Manual approval)
 
 
 
 
☸️ Kubernetes Deployment
 
Kustomize Structure
 
plaintext
  
k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── pdb.yaml          # Pod Disruption Budget
│   └── kustomization.yaml
└── overlays/
    ├── dev/
    │   ├── cpu-limits.yaml
    │   └── kustomization.yaml
    ├── uat/
    │   ├── replicas.yaml
    │   └── kustomization.yaml
    └── prod/
        ├── hpa.yaml       # Auto-scaling
        ├── pdb.yaml
        └── kustomization.yaml
 
 
Deployment Commands
 
bash
  
# Deploy to environment
kubectl apply -k k8s/overlays/dev

# Verify deployment
kubectl get pods -n dev
kubectl get svc -n dev
kubectl describe ingress -n dev

# Check rollout status
kubectl rollout status deployment/app -n dev

# Rollback if needed
kubectl rollout undo deployment/app -n dev
 
 
Production Hardening
 
yaml
  
# hpa.yaml — Auto-scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
---
# pdb.yaml — Pod Disruption Budget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: my-app
 
 
 
 
🧪 UAT Environment
 
UAT Deployment Checklist
 
Namespace created:  kubectl create namespace uat 
Database provisioned & migrated
Secrets populated (never commit — use ExternalSecrets/Secrets Manager)
Ingress/DNS configured
Smoke tests pass
API contract tests pass
User workflow scenarios validated
Performance baseline established
Business stakeholder signs off ✅
 
 
 
🤖 AI Integration (Vertex MCP)
 
Architecture Overview
 
plaintext
  
   User / Agent
       │
       ▼
   MCP Client
       │
       ▼
   MCP Server ◄─── Auth: Service Account / Workload Identity
       │
       ├───► Vertex AI Gemini  (Generate Content)
       ├───► Vertex Embeddings  (Semantic Search)
       ├───► BigQuery          (Data Analytics)
       └──► Cloud Storage     (Knowledge Retrieval)
 
 
MCP Configuration
 
yaml
  
# mcp-config.yaml
apiVersion: mcp.vertexai/v1
kind: MCPServer
metadata:
  name: vertex-ai
spec:
  provider: google-cloud
  project: my-gcp-project
  region: asia-southeast1
  auth:
    type: workload_identity
  tools:
    - name: generate_content
      model: gemini-2.0-flash
    - name: get_embeddings
      model: text-embedding-005
    - name: bigquery.query
      enabled: true
    - name: storage.read
      buckets: ["docs-knowledge-base"]
  security:
    allow_from:
      - kubernetes-namespace:dev
      - kubernetes-namespace:uat
 
 
 
 
🔒 Security & Compliance
 
Security Gates — Integrated in Pipeline
 
Gate Tool When Fails Pipeline? 
Secret Scanning GitHub Secret Scanning Push/PR ✅ Yes 
Dependency Review Dependabot + Review PR ✅ Yes 
Code Scanning CodeQL Daily + PR ⚠️ Warning 
Image Vulnerability Trivy Build ✅ CRITICAL/HIGH only 
License Check FOSSA Scheduled ⚠️ Warning 
 
Secrets Management — ⚠️ CRITICAL RULE
 
NEVER commit  .env , API keys, tokens, or credentials to Git
 
Where to Store Solution 
Local dev  .env  file — in  .gitignore  
CI/CD GitHub Secrets →  ${{ secrets.NAME }}  
Kubernetes Secrets + External Secrets Operator 
Cloud GCP Secret Manager / AWS Secrets Manager 
 
 
 
🔧 Maintenance & Automation
 
Cron Schedule Template
 
yaml
  
apiVersion: batch/v1
kind: CronJob
metadata:
  name: app-maintenance
spec:
  schedule: "0 2 * * *"   # Daily @ 2 AM UTC
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 3
      template:
        spec:
          restartPolicy: OnFailure
          serviceAccountName: app-maintenance
          containers:
          - name: tasks
            image: my-app:latest
            command: ["/bin/sh", "-c"]
            args:
            - |
              /app/scripts/backup.sh && \
              /app/scripts/cleanup-temp-files.sh && \
              /app/scripts/health-check.sh
 
 
Weekly Maintenance Checklist
 
 git dependabot  — Review dependency updates
Security alerts — Address HIGH/CRITICAL vulnerabilities
CI run history — Investigate flaky tests
Log review — Check for errors/warnings
Disk cleanup — Remove old images/pods
Backup verification — Confirm restore works
 
 
 
📊 Quick Reference
 
Category Command / Action When 
Git Workflow  git checkout -b feat/name  → commit → push → PR Daily dev 
Local Run  docker compose up -d --build  Start dev stack 
Build  make build  /  docker build -t app:tag .  Before deploy 
CI Check All jobs green ✅ Before merge 
Deploy Dev  kubectl apply -k k8s/overlays/dev  Merge to main 
Deploy UAT Tag RC → manual approval →  kubectl apply -k overlays/uat  Pre-release 
Deploy Prod Tag release → approval →  kubectl apply -k overlays/prod  Release 
Status  /summaries  → generate project snapshot Weekly reports 
 
 
 
✅ Pre-Deployment Checklist — Production Release
 
Code Quality
 
All CI jobs passing
Code review approved ✅
No new HIGH/CRITICAL vulnerabilities
Documentation updated
 
Environment
 
Database migrations tested on UAT
Secrets validated
Ingress/DNS ready
Monitoring/Alerts configured
Rollback plan documented & tested
 
Validation
 
Smoke tests pass on UAT
Load/performance baseline met
Business acceptance signed off ✅
Change log finalized
Communication sent to stakeholders
 
 
 
💡 Next Steps: Save this as  skillsbook/README.md  or  skillsbook/00-overview.md  in your repository. Customize tech stack specifics, adjust CI triggers, and add environment details to match your project. Want me to convert this to Obsidian  .md  format with tags and frontmatter? 😊

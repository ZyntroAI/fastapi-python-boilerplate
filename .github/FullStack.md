# FullStack Development & DevOps Skillsbook

> A comprehensive guide for full-stack development, DevOps workflows, Docker, Kubernetes, CI/CD, and AI integration.

---

## Table of Contents

- [Workflow Overview](#workflow-overview)
- [Project Planning](#project-planning)
- [Feature Development](#feature-development)
- Build & Testing
- [Documentation](#documentation)
- Docker & Containerization
- [CI/CD with GitHub Actions](#cicd-with-github-actions)
- [Kubernetes Deployment](#kubernetes-deployment)
- [UAT Environment](#uat-environment)
- [AI Integration (Vertex MCP)](#ai-integration-vertex-mcp)
- Maintenance & Automation
- [Repository Structure](#repository-structure)
- [Quick Reference](#quick-reference)

---

## Workflow Overview

The complete development and deployment lifecycle:

```text
/create-plans → /create-skillsbooks → /feat → /build → /test → /docs → /updates 
→ /docker-compose → /github-actions → /deploy dev → /setup uat → /deploy uat 
→ /deploy prod → /summaries
Command Reference
Command	Purpose
/create-plans	Create implementation plan
/create-skillsbooks	Generate reusable engineering knowledge
/feat	Develop a feature
/build	Build application and artifacts
/test	Run tests and validation
/docs	Create or update documentation
/updates	Review updates and maintenance
/docker-compose	Manage local containers
/github-actions	Configure CI/CD
/deploy dev	Deploy development environment
/setup uat	Prepare UAT environment
/deploy uat	Deploy UAT environment
/deploy prod	Deploy production
/vertex-mcp	Configure Vertex AI/MCP integration
/chores	Perform maintenance
/summaries	Generate project summary
Project Planning
/create-plans
Create an implementation plan before development begins.

Planning Areas:

Requirements analysis
Architecture design
Technology stack selection
Repository structure
Environment strategy
Security requirements
Deployment strategy
Development Areas:

Repository setup
Feature implementation
Testing strategy
Documentation plan
Code review process
Infrastructure Areas:

Docker configuration
Docker Compose setup
Kubernetes manifests
Helm charts
GitHub Actions workflows
CI/CD pipelines
Monitoring setup
Feature Development
/feat
Define and implement a new application feature.

Workflow:

Define requirements
Design implementation
Implement source code
Add tests
Update documentation
Run validation
Commit changes
Example:

git checkout -b feat/new-feature

git add .
git commit -m "feat: add new feature"
git push origin feat/new-feature
Build & Testing
/build
Build the application and deployment artifacts.

Commands:

make build
make lint
make test
docker build -t my-app:latest .
Responsibilities:

Compile application source
Validate dependencies
Run linting checks
Execute tests
Build production artifacts
Create container images
/test
Run automated validation before deployment.

Test Layers:

Unit Tests
    ↓
Integration Tests
    ↓
API Tests
    ↓
Container Tests
    ↓
Smoke Tests
    ↓
UAT
Example:

make lint
make test
Documentation
/docs
Maintain comprehensive project documentation.

Recommended Structure:

docs/
├── architecture.md
├── api.md
├── development.md
├── deployment.md
├── troubleshooting.md
└── runbook.md
Documentation Should Cover:

System architecture
API specifications
Development setup
Deployment procedures
Configuration options
Troubleshooting guides
Operations manual
Disaster recovery plans
Docker & Containerization
/docker-compose
Example local development stack:

services:
  api:
    build:
      context: ./backend
    ports:
      - "8080:8080"
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
Docker Commands:

# Start services
docker compose up -d

# Check services
docker compose ps

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild
docker compose build --no-cache
Docker Scaling
Horizontal Scaling:

docker compose up --scale api=3
Architecture:

             Load Balancer
                  |
        +---------+---------+
        |         |         |
        v         v         v
      API-1     API-2     API-3
        |         |         |
        +---------+---------+
                  |
                  v
              Database
                  |
                  v
                Cache
Note: In production, use proper load-balancing and service-discovery layers rather than relying solely on Docker Compose scaling.

CI/CD with GitHub Actions
/github-actions
Recommended Workflow Structure:

.github/
└── workflows/
    ├── ci.yml
    ├── secret-scan.yml
    ├── dependency-review.yml
    ├── deploy-dev.yml
    ├── deploy-uat.yml
    └── release.yml
CI Example:

name: CI

on:
  push:
    branches:
      - main
  pull_request:

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
Kubernetes Deployment
Kubernetes Structure
Recommended Layout:

k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
│
└── overlays/
    ├── dev/
    ├── uat/
    └── prod/
Deploy Development:

kubectl apply -k k8s/overlays/dev
kubectl get pods -n dev
kubectl rollout status deployment/app -n dev
Kubernetes Scaling
Manual Scaling:

kubectl scale deployment app --replicas=5 -n dev
Horizontal Pod Autoscaler:

kubectl autoscale deployment app \
  --min=2 \
  --max=10 \
  --cpu-percent=70
Helm
Example Deployment:

helm upgrade --install app ./helm/app \
  --namespace dev \
  --create-namespace \
  -f values-dev.yaml
Recommended Helm Structure:

helm/
└── app/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── deployment.yaml
        ├── service.yaml
        ├── ingress.yaml
        └── configmap.yaml
UAT Environment
/setup uat
Prepare the User Acceptance Testing environment.

Setup Commands:

kubectl create namespace uat
kubectl apply -k k8s/overlays/uat
kubectl get pods -n uat
kubectl rollout status deployment/app -n uat
UAT Checklist
Environment:

 Namespace created
 Database configured
 Storage configured
 Secrets configured
 Network policies configured
 Ingress configured
Testing:

 Smoke tests
 API tests
 Integration tests
 User workflows
 Acceptance tests
Approval:

 UAT completed
 Business validation completed
 Production readiness confirmed
 Release approved
AI Integration (Vertex MCP)
/vertex-mcp
Conceptual Architecture:

                  AI Agent
                     |
                     | MCP
                     v
                 MCP Server
                     |
                     v
                 Vertex AI
                     |
          +----------+----------+
          |          |          |
          v          v          v
       Gemini    Embeddings   BigQuery
          |
          v
     Cloud Storage
          |
          v
       Kubernetes
Example Configuration:

mcp:
  server: vertex-ai
  provider: google-cloud
  project: my-project
  region: asia-southeast1
  tools:
    - generate_content
    - embeddings
    - cloud_storage
    - bigquery
Security Note: Treat credentials, API keys, service-account files, and production secrets as external configuration. Do not commit secrets to the repository.

Maintenance & Automation
/chores
Perform technical maintenance and housekeeping.

Dependencies:

Update packages
Apply security patches
Review deprecated dependencies
Update lockfiles
CI/CD:

Clean workflows
Improve caching
Review build performance
Review deployment permissions
Repository:

Remove unused files
Improve project structure
Refactor technical debt
Update documentation
Security:

Review secrets
Review permissions
Run secret scanning
Review dependency vulnerabilities
Cron Jobs
Linux Cron Examples:

# Backup at 02:00
0 2 * * * /opt/app/scripts/backup.sh

# Health check every 5 minutes
*/5 * * * * /opt/app/scripts/health-check.sh

# Weekly report Monday at 08:00
0 8 * * 1 /opt/app/scripts/report.sh
Kubernetes CronJob:

apiVersion: batch/v1
kind: CronJob
metadata:
  name: app-maintenance
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: maintenance
              image: my-app:latest
              command:
                - /bin/sh
                - -c
                - /app/scripts/maintenance.sh
/change-appname
Rename the application consistently across the repository.

Rename Checklist:

 package.json
 Environment variables
 Docker image names
 Docker Compose
 Kubernetes metadata
 Helm values
 GitHub Actions
 Documentation
 Monitoring configuration
/summaries
Generate a project status summary.

Example:

Area	Status	Next Action
Feature	Development	Complete implementation
Build	Validation	Run CI
Dev	Active	Smoke test
UAT	Preparing	Deploy UAT
Production	Pending	UAT approval
A good summary should include:

Current state
Completed work
Remaining work
Known issues
Risks
Deployment status
Next actions
Release readiness
Repository Structure
Recommended Structure:

.
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── secret-scan.yml
│       ├── dependency-review.yml
│       ├── deploy-dev.yml
│       ├── deploy-uat.yml
│       └── release.yml
│
├── backend/
│
├── frontend/
│
├── docker/
│
├── k8s/
│   ├── base/
│   └── overlays/
│       ├── dev/
│       ├── uat/
│       └── prod/
│
├── helm/
│   └── app/
│
├── scripts/
│   ├── backup.sh
│   ├── cleanup.sh
│   ├── health-check.sh
│   └── maintenance.sh
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── development.md
│   ├── deployment.md
│   ├── troubleshooting.md
│   └── runbook.md
│
├── skillsbook/
│   ├── 00-overview.md
│   ├── 01-foundation.md
│   ├── 02-development.md
│   ├── 03-testing.md
│   ├── 04-devops.md
│   ├── 05-kubernetes.md
│   ├── 06-ai-vertex-mcp.md
│   ├── 07-security.md
│   ├── 08-troubleshooting.md
│   └── 09-best-practices.md
│
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── README.md
Environment Strategy
Use separate environments for development, UAT, and production.

                 Git Repository
                       |
                       v
                  GitHub Actions
                       |
          +------------+------------+
          |            |            |
          v            v            v
         DEV          UAT          PROD
          |            |            |
          v            v            v
       Testing      Acceptance    Release
Environment	Purpose	Deployment
dev	Development and integration	Automatic
uat	User acceptance testing	Controlled
prod	Production	Approval required
Quick Reference
PLAN
PLAN
  |
  +-- /create-plans
  |
  +-- /create-skillsbooks
DEVELOP
DEVELOP
  |
  +-- /feat
  +-- /build
  +-- /test
  +-- /docs
  +-- /updates
CONTAINER
CONTAINER
  |
  +-- /docker-compose
  +-- Docker build
CI/CD
CI/CD
  |
  +-- /github-actions
KUBERNETES
KUBERNETES
  |
  +-- /deploy dev
  +-- /setup uat
  +-- /deploy uat
  +-- /deploy prod
AI
AI
  |
  +-- /vertex-mcp
OPERATIONS
OPERATIONS
  |
  +-- /chores
  +-- Cron Jobs
  +-- Scaling
  +-- Monitoring
REPORTING
REPORTING
  |
  +-- /summaries
Release Pipeline
+---------+
|  Plan   |
+----+----+
     |
     v
+---------+
| Feature |
+----+----+
     |
     v
+---------+
|  Build  |
+----+----+
     |
     v
+---------+
|  Test   |
+----+----+
     |
     v
+---------+
| Docker  |
+----+----+
     |
     v
+---------+
|   CI    |
+----+----+
     |
     v
+---------+
|   Dev   |
+----+----+
     |
     v
+---------+
|   UAT   |
+----+----+
     |
     v
+---------+
|  Prod   |
+---------+
Release Validation
make lint
make test
make build
docker build -t my-app:latest .
docker compose up -d
kubectl get pods -n dev
kubectl rollout status deployment/app -n dev
Operational Checklist
Before production release:

 Feature implemented
 Unit tests passing
 Integration tests passing
 Lint passing
 Docker image builds successfully
 Security scanning completed
 Dependencies reviewed
 Dev deployment validated
 UAT deployed
 UAT completed
 Production configuration reviewed
 Database migration reviewed
 Backup verified
 Monitoring configured
 Rollback strategy confirmed
 Production approval received
Skillsbook Areas
Foundation
Git workflows
Coding standards
Architecture patterns
Repository structure
Development
Feature development
Testing strategies
Code review processes
Refactoring techniques
DevOps
Docker containerization
CI/CD pipelines
Container registries
Deployment strategies
Monitoring setups
Kubernetes
Pods and Deployments
Services and ConfigMaps
Secrets management
Ingress controllers
Helm charts
Horizontal Pod Autoscaling
AI
Vertex AI integration
Gemini models
MCP protocols
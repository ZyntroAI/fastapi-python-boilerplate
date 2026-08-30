K8s / Infrastructure Code Guide

ถ้าจะจัด repo ให้ Kubernetes + Infrastructure + CI/CD + Security + Observability ทำงานเป็นระบบ ผมแนะนำให้แยก application code, K8s manifests, และ infrastructure provisioning ออกจากกันชัดเจน ไม่อย่างนั้นสุดท้าย YAML จะกลายเป็นระบบนิเวศที่วิวัฒนาการเองครับ

If the goal is a production-ready Kubernetes + Infrastructure + CI/CD stack, use a layered structure like this.

1. Recommended repository structure

repo/
├── app/
│   ├── api/
│   ├── web/
│   └── worker/
│
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.web
│   └── Dockerfile.worker
│
├── k8s/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   ├── hpa.yaml
│   │   ├── pdb.yaml
│   │   ├── networkpolicy.yaml
│   │   └── kustomization.yaml
│   │
│   └── overlays/
│       ├── dev/
│       │   ├── kustomization.yaml
│       │   └── patches.yaml
│       ├── staging/
│       │   ├── kustomization.yaml
│       │   └── patches.yaml
│       └── production/
│           ├── kustomization.yaml
│           └── patches.yaml
│
├── helm/
│   └── app/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── values-staging.yaml
│       ├── values-production.yaml
│       └── templates/
│
├── infra/
│   ├── terraform/
│   │   ├── modules/
│   │   │   ├── network/
│   │   │   ├── kubernetes/
│   │   │   ├── database/
│   │   │   └── monitoring/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   └── versions.tf
│   │
│   ├── ansible/
│   └── scripts/
│
├── observability/
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── otel/
│
├── security/
│   ├── network-policies/
│   ├── policies/
│   ├── rbac/
│   └── admission/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── security.yml
│       ├── docker.yml
│       ├── terraform.yml
│       ├── k8s-validate.yml
│       └── deploy.yml
│
├── Makefile
├── docker-compose.yml
└── README.md


---

2. Responsibility model

ใช้กฎง่าย ๆ:

Application
    ↓
Docker
    ↓
Kubernetes
    ↓
Cloud Infrastructure
    ↓
Observability / Security

แต่ละ layer มีหน้าที่ไม่ซ้ำกัน

Layer	Responsibility

app/	Business logic
docker/	Container image
k8s/	Runtime configuration
helm/	Kubernetes packaging
terraform/	Cloud infrastructure
security/	Security policies
observability/	Metrics / logs / traces
.github/workflows/	Automation


Kubernetes should deploy workloads. Terraform should provision infrastructure.

ไม่ควรเอา Terraform ไปสร้างทุกอย่างจนกลายเป็น main.tf ขนาดเท่าพระไตรปิฎก และไม่ควรให้ Kubernetes YAML ไปสร้าง cloud networking โดยตรงแบบไร้ขอบเขต


---

3. Kubernetes base

ตัวอย่าง deployment.yaml

apiVersion: apps/v1
kind: Deployment

metadata:
  name: api

spec:
  replicas: 2

  selector:
    matchLabels:
      app: api

  template:
    metadata:
      labels:
        app: api

    spec:
      serviceAccountName: api

      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault

      containers:
        - name: api
          image: ghcr.io/example/api:latest

          ports:
            - containerPort: 8000

          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"

          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000

          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000

          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

หลักสำคัญคือ

requests != limits

readiness != liveness

securityContext != optional


---

4. Service

apiVersion: v1
kind: Service

metadata:
  name: api

spec:
  type: ClusterIP

  selector:
    app: api

  ports:
    - name: http
      port: 80
      targetPort: 8000

Application ภายใน cluster จะเรียก:

http://api

หรือ

http://api.namespace.svc.cluster.local


---

5. HPA

สำหรับ API ที่มี traffic:

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler

metadata:
  name: api

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api

  minReplicas: 2
  maxReplicas: 10

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30

    scaleDown:
      stabilizationWindowSeconds: 300

  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70

สำหรับ AI/API workload สามารถขยายไปถึง:

CPU
Memory
Request rate
Latency
Queue depth
GPU utilization
Token throughput
Provider quota

ตรงนี้เหมาะกับระบบที่คุณกำลังทำเรื่อง AI routing และ cost control มาก เพราะ CPU-based autoscaling อย่างเดียวไม่รู้เรื่อง token economics เลย


---

6. PodDisruptionBudget

apiVersion: policy/v1
kind: PodDisruptionBudget

metadata:
  name: api

spec:
  minAvailable: 1

  selector:
    matchLabels:
      app: api

ช่วยป้องกันไม่ให้ maintenance / node drain ฆ่า pod พร้อมกันหมด


---

7. NetworkPolicy

Default deny เป็น baseline ที่ดี:

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy

metadata:
  name: default-deny

spec:
  podSelector: {}

  policyTypes:
    - Ingress
    - Egress

จากนั้นค่อยเปิดเฉพาะ traffic ที่จำเป็น

Ingress
   ↓
API
   ↓
Redis
   ↓
PostgreSQL

ไม่ใช่:

ทุก Pod → ทุก Pod

เพราะมนุษย์สร้าง network segmentation แล้วมนุษย์อีกกลุ่มหนึ่งก็เปิด 0.0.0.0/0 กลับมาในวันศุกร์ตอน 17:58


---

8. Kustomize

k8s/base/kustomization.yaml

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - namespace.yaml
  - serviceaccount.yaml
  - deployment.yaml
  - service.yaml
  - ingress.yaml
  - hpa.yaml
  - pdb.yaml
  - networkpolicy.yaml

Production:

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: production

resources:
  - ../../base

images:
  - name: ghcr.io/example/api
    newTag: v1.4.2

replicas:
  - name: api
    count: 3

ทำให้:

base
 ├── dev
 ├── staging
 └── production

ใช้ manifest ชุดเดียวกัน แต่ configuration ต่างกัน


---

9. Terraform

Terraform ควรจัดเป็น modules:

terraform/
├── modules/
│   ├── network/
│   ├── cluster/
│   ├── database/
│   ├── redis/
│   └── monitoring/
│
└── environments/
    ├── dev/
    ├── staging/
    └── production/

ตัวอย่าง:

module "network" {
  source = "../../modules/network"

  environment = var.environment
}

module "cluster" {
  source = "../../modules/cluster"

  environment = var.environment
  network_id  = module.network.id
}

Environment:

module "app" {
  source = "../../modules/cluster"

  environment = "production"

  node_count = 3
}

แนวคิดสำคัญ:

modules/
    reusable infrastructure

environments/
    actual deployment configuration


---

10. Secrets

อย่าเก็บ:

stringData:
  OPENAI_API_KEY: "sk-..."

ไว้ใน Git

ใช้:

External Secrets
        ↓
Secret Manager
        ↓
Kubernetes Secret
        ↓
Pod

หรือระบบ secret management ที่เหมาะกับ cloud provider

สำหรับ AI infrastructure ควรแยก:

DATABASE_URL
REDIS_URL

OPENAI_API_KEY
ANTHROPIC_API_KEY
GEMINI_API_KEY

GITHUB_TOKEN

SENTRY_DSN

และกำหนด permission ตาม workload

api → AI providers
worker → queue
migration → database
monitoring → metrics

ไม่ใช่ทุก service ถือ master key ใบเดียวเหมือนกุญแจปราสาท


---

11. Terraform CI

name: Terraform

on:
  pull_request:
    paths:
      - "infra/terraform/**"

  push:
    branches:
      - main
    paths:
      - "infra/terraform/**"

jobs:
  terraform:
    runs-on: ubuntu-latest

    permissions:
      contents: read

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3

      - name: Init
        working-directory: infra/terraform/environments/dev
        run: terraform init

      - name: Format
        run: terraform fmt -check -recursive

      - name: Validate
        working-directory: infra/terraform/environments/dev
        run: terraform validate

      - name: Plan
        working-directory: infra/terraform/environments/dev
        run: terraform plan

Production ควรมี approval gate ก่อน:

PR
 ↓
fmt
 ↓
validate
 ↓
security scan
 ↓
plan
 ↓
review
 ↓
approval
 ↓
apply


---

12. Kubernetes CI

Pipeline:

YAML
 ↓
kubeconform
 ↓
kube-linter
 ↓
OPA / Kyverno
 ↓
security scan
 ↓
Helm template
 ↓
Kustomize build
 ↓
deploy

ตัวอย่าง:

- name: Kustomize build
  run: |
    kubectl kustomize k8s/overlays/dev

- name: Kubernetes validation
  run: |
    kubeconform \
      -strict \
      k8s/overlays/dev


---

13. Image security

CI ควรมี:

Docker build
      ↓
SBOM
      ↓
Vulnerability scan
      ↓
Image signing
      ↓
Registry
      ↓
Kubernetes

และ production cluster ควร reject image ที่ไม่ผ่าน policy

เช่น:

unsigned image       → DENY
critical CVE         → DENY
latest tag           → DENY
root container       → DENY
privileged container → DENY

ใช้ immutable version:

api:v1.4.2

หรือดีกว่า:

api@sha256:<digest>


---

14. Observability

โครงสร้าง:

Application
    │
    ├── Metrics ──────→ Prometheus
    │
    ├── Logs ─────────→ Loki
    │
    └── Traces ───────→ OpenTelemetry
                              │
                              ↓
                           Grafana

Metrics สำคัญสำหรับ AI service:

http_requests_total
http_request_duration_seconds

llm_requests_total
llm_tokens_input_total
llm_tokens_output_total

llm_cost_total
llm_errors_total

cache_hits_total
cache_misses_total

provider_failures_total
circuit_breaker_open_total

นี่จะทำให้ระบบรู้ว่า:

request
 ↓
model
 ↓
tokens
 ↓
cost
 ↓
cache
 ↓
provider
 ↓
latency

ไม่ใช่แค่รู้ว่า HTTP 200 แล้วจบพิธีกรรม


---

15. Recommended production architecture

Internet
                            │
                            ▼
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Ingress      │
                    │ Controller   │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        ┌───────────┐             ┌───────────┐
        │ Web       │             │ API       │
        │ Deployment│             │ Deployment│
        └───────────┘             └─────┬─────┘
                                        │
                    ┌───────────────────┼──────────────────┐
                    ▼                   ▼                  ▼
                ┌───────┐          ┌─────────┐       ┌──────────┐
                │ Redis │          │ Postgres│       │ AI Router│
                └───────┘          └─────────┘       └────┬─────┘
                                                          │
                              ┌───────────────────────────┼─────────────┐
                              ▼                           ▼             ▼
                         Provider A                  Provider B    Provider C

Observability อยู่ด้านข้าง:

┌─────────────────────┐
                  │ OpenTelemetry       │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │ Prometheus / Loki   │
                  │ Grafana             │
                  └─────────────────────┘


---

16. Recommended deployment model

สำหรับ repo ของคุณ ผมจะใช้:

Terraform
    │
    ├── Network
    ├── Kubernetes Cluster
    ├── Database
    ├── Redis
    └── Cloud resources
             │
             ▼
        Kubernetes
             │
             ├── Helm
             ├── Kustomize
             ├── Deployments
             ├── Services
             ├── HPA
             ├── NetworkPolicy
             └── RBAC

แล้ว GitHub Actions เป็น control plane:

Developer
   │
   ▼
GitHub PR
   │
   ├── Unit tests
   ├── Lint
   ├── SAST
   ├── Dependency scan
   ├── Docker scan
   ├── Terraform validation
   ├── Kubernetes validation
   └── Policy validation
          │
          ▼
       Merge
          │
          ▼
       Build image
          │
          ▼
      Sign image
          │
          ▼
       Registry
          │
          ▼
     Deploy to K8s
          │
          ▼
      Monitoring

17. The baseline I would enforce

[Infrastructure]
✓ Terraform
✓ Remote state
✓ Modules
✓ Environment separation

[Kubernetes]
✓ Namespace
✓ RBAC
✓ ServiceAccount
✓ Deployment
✓ Service
✓ Ingress
✓ HPA
✓ PDB
✓ NetworkPolicy
✓ Resource requests/limits
✓ Probes
✓ SecurityContext

[Security]
✓ Secret manager
✓ Non-root containers
✓ Read-only filesystem
✓ Drop capabilities
✓ Image scanning
✓ SBOM
✓ Image signing
✓ Admission policies

[CI/CD]
✓ GitHub Actions
✓ Terraform plan/apply
✓ K8s validation
✓ Helm lint
✓ Kustomize build
✓ Container scanning
✓ Automated deployment

[Observability]
✓ Prometheus
✓ Grafana
✓ Loki
✓ OpenTelemetry
✓ Alerting

[AI-specific]
✓ Model router
✓ Provider fallback
✓ Circuit breaker
✓ Semantic cache
✓ Token accounting
✓ Cost accounting
✓ Per-tenant budget
✓ Rate limiting
✓ Cost anomaly detection

สรุป: โครงสร้างนี้เหมาะกับการต่อยอดไปเป็น production-grade AI platform มากกว่าการมีแค่ deployment.yaml กับ docker-compose.yml เพราะ infrastructure, runtime, security, deployment และ observability ถูกแยกเป็น layer แต่ยังเชื่อมกันผ่าน CI/CD อย่างชัดเจน

English: This structure gives you a clean path from local Docker Compose → Kubernetes → cloud infrastructure → secure CI/CD → observability → AI cost/routing control, without turning the repository into a YAML archaeological site.
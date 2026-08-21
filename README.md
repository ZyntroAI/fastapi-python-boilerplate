🚀 FastAPI Production Blueprint: Dual Deployment

Vercel Serverless + Kubernetes

โครงสร้างนี้เหมาะสำหรับ FastAPI ที่ต้องการ codebase เดียว แต่ deploy ได้ 2 runtime โดยแยก concerns ระหว่าง Vercel สำหรับ lightweight serverless/testing และ Kubernetes สำหรับ production scale อย่างชัดเจน

This blueprint keeps one FastAPI application while separating deployment concerns:

FastAPI Application
                            │
              ┌─────────────┴─────────────┐
              │                           │
          Vercel                      Kubernetes
        Serverless                  Production
              │                           │
        api/index.py                 Docker Image
                                      │
                                      ▼
                                  Deployment
                                      │
                                  Service
                                      │
                                  Ingress
                                      │
                              ┌───────┴───────┐
                              ▼               ▼
                           HPA/Pods       Monitoring


---

1. Project Structure

oauth-fastapi/
│
├── app/
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── callback.py
│   │   └── health.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── oauth_service.py
│   │   ├── token_service.py
│   │   └── user_service.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   └── main.py
│
├── api/
│   └── index.py
│
├── docker/
│   └── Dockerfile
│
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.example.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   └── kustomization.yaml
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   └── test_auth.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-vercel.yml
│       └── deploy-k8s.yml
│
├── .dockerignore
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── vercel.json
└── README.md


---

2. FastAPI Application

app/main.py

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.callback import router as callback_router
from app.api.health import router as health_router

app = FastAPI(
    title="OAuth FastAPI",
    version="1.0.0",
)

app.include_router(health_router, tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(callback_router, prefix="/auth", tags=["callback"])


@app.get("/")
async def root():
    return {
        "service": "oauth-fastapi",
        "status": "ok",
    }


---

3. Configuration

ใช้ pydantic-settings เพื่อให้ configuration มาจาก environment แทนการ hard-code secrets

app/core/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "oauth-fastapi"
    environment: str = "development"

    oauth_client_id: str
    oauth_client_secret: str
    oauth_redirect_uri: str

    jwt_secret: str

    cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

Production:

Environment variables
        │
        ├── Vercel Environment Variables
        │
        └── Kubernetes Secret

ไม่ควร commit:

.env
secret.yaml
private keys
OAuth client secrets
JWT secrets


---

4. Health / Readiness

app/api/health.py

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
    }


@router.get("/ready")
async def ready():
    return {
        "status": "ready",
    }

ใช้แยก:

/health
    │
    └── Process is alive

/ready
    │
    └── Application is ready

Kubernetes จะใช้ /ready เป็น readiness probe และ /health เป็น liveness probe


---

5. Vercel Serverless

api/index.py

from app.main import app

__all__ = ["app"]

vercel.json

{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}

Flow:

HTTP Request
     │
     ▼
Vercel
     │
     ▼
api/index.py
     │
     ▼
app.main:app

Vercel เหมาะกับ preview/testing และ workloads ที่ไม่ต้องการ persistent process


---

6. Docker Production Image

docker/Dockerfile

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd \
    --create-home \
    --shell /usr/sbin/nologin \
    appuser

USER appuser

EXPOSE 8000

CMD [
  "uvicorn",
  "app.main:app",
  "--host",
  "0.0.0.0",
  "--port",
  "8000"
]

Production image:

Dockerfile
    │
    ▼
FastAPI
    │
    ▼
Uvicorn
    │
    ▼
Container


---

7. Kubernetes Namespace

k8s/namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: oauth-fastapi


---

8. ConfigMap

k8s/configmap.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: oauth-fastapi-config
  namespace: oauth-fastapi
data:
  APP_NAME: "oauth-fastapi"
  ENVIRONMENT: "production"
  OAUTH_REDIRECT_URI: "https://api.example.com/auth/callback"

Non-sensitive configuration belongs here.

Secrets do not.


---

9. Secret

k8s/secret.example.yaml

apiVersion: v1
kind: Secret
metadata:
  name: oauth-fastapi-secret
  namespace: oauth-fastapi
type: Opaque
stringData:
  OAUTH_CLIENT_ID: "replace-me"
  OAUTH_CLIENT_SECRET: "replace-me"
  JWT_SECRET: "replace-me"

ใช้เป็น example เท่านั้น:

secret.example.yaml
       │
       └── Documentation only

Production
       │
       └── External Secret Manager / sealed secret / platform secret


---

10. Kubernetes Deployment

k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: oauth-fastapi
  namespace: oauth-fastapi
spec:
  replicas: 3

  selector:
    matchLabels:
      app: oauth-fastapi

  template:
    metadata:
      labels:
        app: oauth-fastapi

    spec:
      containers:
        - name: api
          image: ghcr.io/zyntroai/oauth-fastapi:latest

          ports:
            - containerPort: 8000

          envFrom:
            - configMapRef:
                name: oauth-fastapi-config

            - secretRef:
                name: oauth-fastapi-secret

          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"

            limits:
              cpu: "500m"
              memory: "512Mi"

          livenessProbe:
            httpGet:
              path: /health
              port: 8000

            initialDelaySeconds: 10
            periodSeconds: 10

          readinessProbe:
            httpGet:
              path: /ready
              port: 8000

            initialDelaySeconds: 5
            periodSeconds: 5

          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true


---

11. Kubernetes Service

k8s/service.yaml

apiVersion: v1
kind: Service
metadata:
  name: oauth-fastapi
  namespace: oauth-fastapi
spec:
  selector:
    app: oauth-fastapi

  ports:
    - port: 80
      targetPort: 8000

  type: ClusterIP


---

12. Ingress

k8s/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: oauth-fastapi
  namespace: oauth-fastapi

  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"

spec:
  ingressClassName: nginx

  rules:
    - host: api.example.com

      http:
        paths:
          - path: /
            pathType: Prefix

            backend:
              service:
                name: oauth-fastapi
                port:
                  number: 80


---

13. Horizontal Pod Autoscaler

k8s/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: oauth-fastapi
  namespace: oauth-fastapi

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: oauth-fastapi

  minReplicas: 3
  maxReplicas: 20

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

    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80


---

14. Kustomization

k8s/kustomization.yaml

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: oauth-fastapi

resources:
  - namespace.yaml
  - configmap.yaml
  - deployment.yaml
  - service.yaml
  - ingress.yaml
  - hpa.yaml

Deploy:

kubectl apply -k k8s/


---

15. CI

.github/workflows/ci.yml

name: FastAPI CI

on:
  pull_request:
    branches:
      - main
      - develop
      - "release/**"

  push:
    branches:
      - main
      - develop

permissions:
  contents: read

jobs:
  test:
    name: Python Tests
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version:
          - "3.11"
          - "3.12"
          - "3.13"

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: ruff check .

      - name: Test
        run: pytest -q


---

16. Dual Deployment

GitHub
                       │
                       ▼
                    CI/CD
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
          Vercel                GHCR
             │                   │
       Serverless             Docker
             │                   │
             │                   ▼
             │               Kubernetes
             │                   │
             │            ┌──────┴──────┐
             │            ▼             ▼
             │          Service        HPA
             │            │
             │          Ingress
             │            │
             └───────┬────┘
                     ▼
                  FastAPI

Environment strategy

Environment	Runtime	Purpose

Preview	Vercel	PR/preview
Dev	Kubernetes	Integration
UAT	Kubernetes	Acceptance
Production	Kubernetes	Scale
Emergency	Vercel	Temporary fallback



---

17. Production Rules

Production
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
          GitHub CI            Security
              │                   │
        ┌─────┼─────┐       ┌─────┼─────┐
        ▼     ▼     ▼       ▼     ▼     ▼
      Lint   Test  Build   SAST  SCA  Secrets
        │     │     │       │     │     │
        └─────┴─────┴───────┴─────┴─────┘
                        │
                        ▼
                   Docker Image
                        │
                        ▼
                       GHCR
                        │
                        ▼
                   Kubernetes
                        │
                  ┌─────┴─────┐
                  ▼           ▼
                 HPA       Monitoring

จุดที่ควรเพิ่มใน production จริงคือ PostgreSQL/Redis, external secret manager, TLS/cert-manager, Prometheus/Grafana, image scanning, NetworkPolicy และ rolling deployment โดยเฉพาะ OAuth/JWT ไม่ควรผูก secret storage เข้ากับ Git repository เพราะนั่นเป็นวิธีที่มนุษย์ใช้เปลี่ยน incident เล็ก ๆ ให้กลายเป็น incident ใหญ่

I can also turn this blueprint into a ready-to-commit repository package with the FastAPI files, Docker/K8s manifests, tests, and GitHub Actions wired together.

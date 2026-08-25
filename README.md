**ได้ครับ ลองใหม่**

นี่คือ **README ที่ถูกแก้ไขและทำความสะอาดแล้ว**  
(ตัดส่วนที่ติดมาจากบทสนทนาก่อนหน้านี้ออก และจัดรูปแบบให้อ่านง่ายขึ้น)

---

```markdown
# 🚀 FastAPI Production Blueprint: Dual Deployment

**Vercel Serverless + Kubernetes**

โครงสร้างนี้เหมาะสำหรับ FastAPI ที่ต้องการ **codebase เดียว** แต่ deploy ได้ 2 runtime  
โดยแยก concerns ระหว่าง Vercel (lightweight serverless/testing) และ Kubernetes (production scale) อย่างชัดเจน

```
FastAPI Application
            │
  ┌─────────┴─────────┐
  │                   │
Vercel            Kubernetes
Serverless        Production
  │                   │
api/index.py      Docker Image
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
```

---

## 1. Project Structure

```
oauth-fastapi/
│
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── callback.py
│   │   └── health.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── oauth_service.py
│   │   ├── token_service.py
│   │   └── user_service.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
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
```

---

## 2. FastAPI Application

**`app/main.py`**

```python
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
```

---

## 3. Configuration

ใช้ `pydantic-settings` เพื่อให้ configuration มาจาก environment แทนการ hard-code secrets

**`app/core/config.py`**

```python
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
```

**Production Environment Variables**
- Vercel Environment Variables
- Kubernetes Secret

**ห้าม commit**
- `.env`
- `secret.yaml`
- private keys
- OAuth client secrets
- JWT secrets

---

## 4. Health / Readiness

**`app/api/health.py`**

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready():
    return {"status": "ready"}
```

| Endpoint   | ใช้ทำอะไร                  |
|------------|---------------------------|
| `/health`  | Process is alive (Liveness) |
| `/ready`   | Application is ready (Readiness) |

Kubernetes ใช้ `/ready` เป็น readiness probe และ `/health` เป็น liveness probe

---

## 5. Vercel Serverless

**`api/index.py`**
```python
from app.main import app
__all__ = ["app"]
```

**`vercel.json`**
```json
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
```

Vercel เหมาะกับ preview/testing และ workloads ที่ไม่ต้องการ persistent process

---

## 6. Docker Production Image

**`docker/Dockerfile`**

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 7–14. Kubernetes Manifests

| ไฟล์                      | หน้าที่                          |
|---------------------------|----------------------------------|
| `namespace.yaml`          | สร้าง Namespace                  |
| `configmap.yaml`          | Non-sensitive config             |
| `secret.example.yaml`     | ตัวอย่าง Secret (ห้ามใช้จริง)    |
| `deployment.yaml`         | Deployment + Probes + SecurityContext |
| `service.yaml`            | ClusterIP Service                |
| `ingress.yaml`            | Ingress (nginx)                  |
| `hpa.yaml`                | Horizontal Pod Autoscaler        |
| `kustomization.yaml`      | รวมทุกอย่างด้วย Kustomize        |

**Deploy**
```bash
kubectl apply -k k8s/
```

---

## 15. CI

**`.github/workflows/ci.yml`**
- รันบน PR และ push ไปยัง `main` / `develop`
- ทดสอบ Python 3.11 / 3.12 / 3.13
- Lint ด้วย `ruff`
- Test ด้วย `pytest`

---

## 16. Dual Deployment Strategy

| Environment | Runtime     | Purpose              |
|-------------|-------------|----------------------|
| Preview     | Vercel      | PR / Preview         |
| Dev         | Kubernetes  | Integration          |
| UAT         | Kubernetes  | Acceptance           |
| Production  | Kubernetes  | Scale                |
| Emergency   | Vercel      | Temporary fallback   |

---

## 17. Production Rules

จุดที่ควรเพิ่มใน production จริง:
- PostgreSQL / Redis
- External Secret Manager
- TLS / cert-manager
- Prometheus / Grafana
- Image scanning
- NetworkPolicy
- Rolling deployment

> **สำคัญ**: OAuth / JWT secrets **ห้าม** เก็บใน Git repository

---

ต้องการให้เพิ่มส่วนไหนต่อไหม? เช่น:
- ส่วน OpenAI Terms of Use
- Installation / Getting Started
- Environment Variables ตัวอย่าง
- หรือปรับโครงสร้างใด ๆ

บอกได้เลยครับ

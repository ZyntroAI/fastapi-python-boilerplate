ถ้าคุณใช้ **FastAPI** และวางแผนให้รองรับทั้ง **Vercel** (สำหรับ Serverless) และ **Kubernetes** (Production Scale) ผมแนะนำให้จัดโครงสร้างโปรเจกต์ตั้งแต่แรกเลย เพื่อไม่ต้องแก้ภายหลัง

## โครงสร้างโปรเจกต์

```text
oauth-fastapi/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── callback.py
│   │   └── health.py
│   │
│   ├── services/
│   │   ├── oauth_service.py
│   │   ├── token_service.py
│   │   └── user_service.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   └── main.py
│
├── api/
│   └── index.py              # Vercel Entry
│
├── docker/
│   └── Dockerfile
│
├── k8s/
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── secret.example.yaml
│
├── helm/
│   └── oauth-app/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── docker.yml
│       ├── vercel.yml
│       └── kubernetes.yml
│
├── vercel.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

# Vercel

### api/index.py

```python
from app.main import app

handler = app
```

---

### vercel.json

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
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 60
    }
  }
}
```

สำหรับ Hobby Plan สามารถใช้ `maxDuration: 60` ได้ (ขึ้นกับข้อจำกัดของแพ็กเกจในช่วงเวลานั้น)

---

# Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
```

---

# docker-compose

```yaml
version: "3.9"

services:

  api:
    build: .
    ports:
      - "8000:8000"

    env_file:
      - .env
```

---

# Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: oauth-api

spec:
  replicas: 2

  selector:
    matchLabels:
      app: oauth

  template:

    metadata:
      labels:
        app: oauth

    spec:

      containers:

      - name: oauth

        image: ghcr.io/your-org/oauth-api:latest

        ports:

        - containerPort: 8000
```

---

# Service

```yaml
apiVersion: v1

kind: Service

metadata:
  name: oauth-service

spec:

  selector:
    app: oauth

  ports:

  - port: 80
    targetPort: 8000

  type: ClusterIP
```

---

# Ingress

```yaml
apiVersion: networking.k8s.io/v1

kind: Ingress

metadata:
  name: oauth

spec:

  rules:

  - host: oauth.example.com

    http:

      paths:

      - path: /

        pathType: Prefix

        backend:

          service:

            name: oauth-service

            port:

              number: 80
```

---

# GitHub Actions

```text
Push

↓

Lint (ruff)

↓

Black

↓

Pytest

↓

Bandit

↓

Build Docker

↓

Push GHCR

↓

Deploy Vercel

↓

Deploy Kubernetes
```

ตัวอย่างไฟล์ workflow:

```text
.github/workflows/

ci.yml
docker.yml
vercel.yml
kubernetes.yml
security.yml
```

---

# Secrets

ใช้ Environment Variables แทนการฝังค่าลงในโค้ด

```text
CLIENT_ID
CLIENT_SECRET
REDIRECT_URI

JWT_SECRET

DATABASE_URL

REDIS_URL
```

บน Kubernetes ให้เก็บไว้ใน `Secret` ส่วนบน Vercel ให้กำหนดผ่าน Environment Variables ของโปรเจกต์

---

# Monitoring

แนะนำเพิ่ม endpoint

```
GET /health
GET /ready
GET /metrics
```

พร้อมรองรับ

* Prometheus
* Grafana
* OpenTelemetry
* Loki
* Jaeger

---

## Roadmap ที่แนะนำ

```text
Phase 1
✓ FastAPI
✓ OAuth2 + PKCE
✓ Docker
✓ GitHub Actions

Phase 2
✓ Vercel Deployment
✓ GHCR Image
✓ PostgreSQL
✓ Redis

Phase 3
✓ Kubernetes
✓ Helm Chart
✓ Horizontal Pod Autoscaler
✓ Prometheus
✓ Grafana
✓ Loki

Phase 4
✓ Terraform
✓ GitOps (Argo CD หรือ Flux)
✓ Secrets Manager
✓ Multi-environment (dev / staging / production)
```

แนวทางนี้ช่วยให้โปรเจกต์เดียวสามารถพัฒนาและทดสอบบน **Vercel** ได้อย่างรวดเร็ว และเมื่อระบบเติบโต ก็สามารถย้ายไป **Kubernetes** โดยแทบไม่ต้องปรับโครงสร้างโค้ดใหม่ เพราะแยกส่วนของแอป การตั้งค่า และการ deploy ไว้ตั้งแต่ต้น.

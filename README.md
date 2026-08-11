🚀 FastAPI Production Blueprint: Dual
Deployment (Vercel Serverless &
Kubernetes)
คมู่ อื นร
ี้
ะบรุ ายละเอยีดและโคด้ ตวัอยา่ งสำ หรับการตงั้คา่ โปรเจกต์FastAPI ใหร้องรับการ Deploy บน
Vercel สำ หรับงานทดสอบ/Serverless และขยายขดี ความสามารถไปยงั Kubernetes (K8s) สำ หรับ
ระบบระดบั Production Scale
📁 1. โครงสราง้ โปรเจกต์(Project Directory Structure)
oauth-fastapi/
│
├── app/
│ ├── api/
│ │ ├── __init__.py
│ │ ├── auth.py # OAuth2 + PKCE endpoints
│ │ ├── callback.py # OAuth Callback handler
│ │ └── health.py # Health, Readiness, Metrics endpoints
│ │
│ ├── services/
│ │ ├── __init__.py
│ │ ├── oauth_service.py # บริการจัดการ OAuth2 Flow
│ │ ├── token_service.py # บริการจัดการ JWT / Tokens
│ │ └── user_service.py # บริการจัดการข้อมูลผู้ใช้
│ │
│ ├── core/
│ │ ├── __init__.py
│ │ ├── config.py # App Settings (pydantic-settings)
│ │ ├── security.py # Security utilities
│ │ └── logging.py # Logging Configuration
│ │
│ └── main.py # Main Application Entry Point
│
├── api/
│ └── index.py # Vercel Serverless Handler
│
├── docker/
│ └── Dockerfile
│
├── k8s/
│ ├── namespace.yaml
│ ├── configmap.yaml
│ ├── secret.example.yaml
app.include_router(health.router, tags=["Monitoring"])
@app.get("/")
def read_root():
return {
"message": "ยินดีต้อนรับสู่ FastAPI OAuth2 Service",
"environment": settings.ENVIRONMENT,
"docs": "/docs"
}
⚡ 3. Vercel Configuration (Serverless)
api/index.py
from app.main import app
# Handler สำหรับ Vercel Serverless Function
handler = app
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
],
"functions": {
"api/index.py": {
"maxDuration": 60
}
}
}
🐳 4. Docker & Containerization
Dockerfile
FROM python:3.13-slim
# ตั้งค่าไม่ให้สร้างไฟล์ .pyc และพิมพ์ log ทันที
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# ติดตั้ง Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# คัดลอก ซอร์สโค้ดทั้งหมด
COPY . .
# เปิดพอร์ต 8000
EXPOSE 8000
# คำสั่งสำหรับรันระบบ
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
docker-compose.yml
version: "3.9"
services:
api:
build: .
ports:
- "8000:8000"
env_file:
- .env
volumes:
- .:/app
environment:
- ENVIRONMENT=development
☸️ 5. Kubernetes Manifests
k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: oauth-api
namespace: oauth-app
labels:
app: oauth-api
spec:
replicas: 2
selector:
matchLabels:
app: oauth-api
template:
metadata:
labels:
app: oauth-api
spec:
containers:
- name: oauth-api
image: ghcr.io/your-org/oauth-api:latest
imagePullPolicy: Always
ports:
- containerPort: 8000
envFrom:
- configMapRef:
name: oauth-config
- secretRef:
name: oauth-secret
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
resources:
requests:
memory: "128Mi"
cpu: "100m"
limits:
memory: "512Mi"
cpu: "500m"
k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
name: oauth-service
namespace: oauth-app
spec:
type: ClusterIP
selector:
app: oauth-api
ports:
- port: 80
targetPort: 8000
protocol: TCP
name: http
k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
name: oauth-ingress
namespace: oauth-app
annotations:
kubernetes.io/ingress.class: "nginx"
cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
tls:
- hosts:
- oauth.example.com
secretName: oauth-tls
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
🤖 6. CI/CD Pipelines (GitHub Actions)
.github/workflows/ci.yml
name: Continuous Integration
on:
push:
branches: [ main, dev ]
pull_request:
branches: [ main ]
jobs:
lint-and-test:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v4
- name: Set up Python
uses: actions/setup-python@v5
with:
python-version: '3.13'
- name: Install Dependencies
run: |
python -m pip install --upgrade pip
pip install ruff pytest security-scanner
if [ -f requirements.txt ]; then pip install -r
requirements.txt; fi
- name: Lint with Ruff
run: ruff check .
- name: Test with Pytest
run: pytest
🔒 7. Secrets & Environment Variables
สำ หรับการใชง้านจรงิ ใหแ้ยกการจัดการ Environment Variables และ Secrets ดงัน:
ี้
Key Variable คำ อธบิ าย ตวัอยา่ งคา่ บน Dev Vercel Env K8s Target
CLIENT_ID OAuth Client ID client_xyz123 ✅ Add via
Dashboard
Secret
CLIENT_SECRET OAuth Client
Secret
secret_abc456 ✅ Add via
Dashboard
Secret
REDIRECT_URI Callback URL https://api.example✅ Add via ConfigMap
Key Variable คำ อธบิ าย ตวัอยา่ งคา่ บน Dev Vercel Env K8s Target
.com/callback Dashboard
JWT_SECRET Secret Key สำ หรับ
Sign JWT
super-secret-jwt-k
ey
✅ Add via
Dashboard
Secret
DATABASE_URL Connection String
ไปยงั DB
postgresql://user:p
ass@host/db
✅ Add via
Dashboard
Secret
REDIS_URL Connection String
ไปยงั Redis
redis://redis:6379/
0
✅ Add via
Dashboard
ConfigMap/Secret
📊 8. Observability & Monitoring Strategy
ในระบบ Kubernetes Production Scale แนะนำ ตงั้คา่ Monitoring Stack ดงัน:
ี้
1. Metrics Collection (Prometheus & Grafana):
○ ใช ้prometheus-fastapi-instrumentator เพอ
ื่ สง่ ออก HTTP Metrics เชน่ Request
Latency, Error Rate (4xx, 5xx), Request Counter ไปยงั Prometheus
2. Log Aggregation (Loki / Fluentd):
○ ให้FastAPI พมิ พ์Log เป็น JSON Format ออกทาง stdout/stderr เพอ
ื่ ให้Promtail/Loki
เกบ็ ขอ้มลู log เขา้สศู่ นู ยก์ ลาง
3. Tracing (OpenTelemetry & Jaeger):
○ เพม
ิ่ OpenTelemetry Middleware ใน FastAPI เพอ
ื่
ทำ Distributed Tracing สำ หรับ
วเิคราะห์Latency ในการเรยี กไปยงั Database หรอื Auth Server
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
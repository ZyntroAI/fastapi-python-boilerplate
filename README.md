# 🧠 FastAPI Python Boilerplate — AI‑Driven DevOps Stack

### 🚀 Overview
A **production‑ready FastAPI boilerplate** integrating:
- 🧩 **LangGraph AI Agent** — query SQL databases using natural language  
- 💳 **Stripe Payment Integration** — secure, scalable payment flow  
- ⚙️ **Helm + Kubernetes CI/CD** — automated deployment and scaling  
- 🌐 **Traefik Routing** — seamless microservice orchestration  

---

### ⚙️ Getting Started

#### Requirements
- Python 3.11+
- Docker Desktop 4.43+ or Docker Engine
- Docker Compose 2.38.1+ (Linux)
- Optional GPU for local inference

#### Quick Start
```bash
git clone https://github.com/ZyntroAI/fastapi-python-boilerplate.git
cd fastapi-python-boilerplate
docker compose up
```

---

### 🔑 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@db:5432/chinook` |
| `OPENAI_API_KEY` | API key for OpenAI inference | `sk-xxxx` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_xxxx` |
| `STRIPE_PUBLIC_KEY` | Stripe publishable key | `pk_live_xxxx` |
| `APP_ENV` | Environment mode | `development` / `production` |

> Store secrets in `.env` or `secret.*` files. Never commit them to Git.

---

### 🧠 Inference Options
Default: local Docker model runner.  
Switch to OpenAI:
```bash
echo "sk-..." > secret.openai-api-key
docker compose down -v
docker compose -f compose.yaml -f compose.openai.yaml up
```

---

### 🧪 Testing Guide
Run unit tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=app tests/
```

Integration tests (requires containers running):
```bash
docker compose exec backend pytest tests/integration
```

---

### ☸️ Kubernetes Deployment (Helm)

#### Install Helm Chart
```bash
helm install fastapi-boilerplate ./helm
```

#### Upgrade Release
```bash
helm upgrade fastapi-boilerplate ./helm
```

#### Values.yaml Highlights
```yaml
replicaCount: 3
image:
  repository: zyntroai/fastapi-boilerplate
  tag: latest
ingress:
  enabled: true
  hosts:
    - host: fastapi.local
      paths: ["/"]
resources:
  limits:
    cpu: 500m
    memory: 512Mi
```

---

### 📜 License
MIT License © 2026 ZyntroAI

---

### 🧠 Credits
- LangGraph  
- FastAPI  
- PostgreSQL  
- Docker Compose  
- Stripe  
- Traefik  
- Helm  

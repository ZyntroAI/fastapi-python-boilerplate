# 🧠 FastAPI Python Boilerplate — AI‑Driven DevOps Stack

[![CI/CD Pipeline](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/ci.yml)
[![CodeQL Analysis](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/codeql.yml)
[![Codecov Coverage](https://codecov.io/gh/ZyntroAI/fastapi-python-boilerplate/branch/main/graph/badge.svg)](https://codecov.io/gh/ZyntroAI/fastapi-python-boilerplate)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/ZyntroAI/fastapi-python-boilerplate/blob/main/LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI 0.100+](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Docker Compose 2.38+](https://img.shields.io/badge/Docker%20Compose-2.38%2B-blue.svg)](https://docs.docker.com/compose/)

---

## 🚀 Overview

**Production‑ready FastAPI boilerplate** with async support, AI agent integration, payments, authentication, container orchestration, and enterprise‑grade DevOps — all configured and ready to deploy.

---

## ✨ Key Features

### 🧠 AI & Backend
- **LangGraph AI Agent** — Query PostgreSQL using natural language
- **FastAPI 0.100+** — Modern async web framework
- **PostgreSQL + SQLAlchemy 2.0 (async)** — Relational database
- **Alembic** — Schema migrations

### 🔐 Authentication & Security
- **Supabase JWT Auth** — HS256 stateless authentication
- **Row‑Level Security (RLS)** — Enabled on all tables
- **Fixed schema exposure** — Migration prevents `pg_pgrst_no_exposed_schemas` warnings

### 💳 Payments & Integrations
- **Stripe** — Secure payment flow & billing
- **OpenAI / Local model** — Switchable inference backends

### ⚙️ DevOps & Deployment
- **Docker Compose** — One‑command local stack
- **Kubernetes + Helm** — Production‑ready manifests & charts
- **Traefik** — Reverse proxy, ingress, load balancing
- **GitHub CI/CD** — Lint → Test → Coverage → Scan → Deploy

### 📡 Enterprise Alerting (Extended)
- ✅ **Slack** — Real‑time notifications
- ✅ **SMS / Phone Calls** — Twilio integration (Thailand numbers supported)
- ✅ **Jira Service Management** — Auto‑create incident tickets
- ✅ **PagerDuty** — On‑call escalation & incident management

---

## 🛠️ Getting Started

### Requirements
- **Python:** 3.11+
- **Docker:** Desktop 4.43+ or Engine + Compose 2.38.1+
- **Optional:** GPU for local LLM inference

### Quick Start
```bash
# Clone
git clone https://github.com/ZyntroAI/fastapi-python-boilerplate.git
cd fastapi-python-boilerplate

# Copy environment
cp .env.example .env
# Edit .env with your secrets

# Start full stack
docker compose up --build
```

### Access
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **Redoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🔑 Environment Variables

### Core Backend
| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@db:5432/chinook` |
| `APP_ENV` | Runtime mode | `development` / `production` |
| `SUPABASE_JWT_SECRET` | JWT verification key | `your-secret-key` |

### AI & Payments
| Variable | Description | Example |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_...` |
| `STRIPE_PUBLIC_KEY` | Stripe publishable key | `pk_live_...` |

### Enterprise Alerts (Optional)
| Variable | Description |
|---|---|
| `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_FROM` | Twilio credentials |
| `ALERT_SMS_TO`, `ALERT_PHONE_TO` | Recipients (comma‑separated) |
| `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`, `JIRA_PROJECT` | Jira integration |
| `PAGERDUTY_ROUTING_KEY` | PagerDuty Events API key |

> 🔒 **Never commit secrets to Git.** Store in `.env`, `secret.*` files, or CI environment secrets.

---

## 🧠 Inference Options

**Default:** Local Docker model container.

**Switch to OpenAI:**
```bash
echo "sk-..." > secret.openai-api-key
docker compose down -v
docker compose -f compose.yaml -f compose.openai.yaml up
```

---

## 🧪 Testing

```bash
# Unit tests
pytest tests/ -v

# Coverage report
pytest --cov=app --cov-report=xml tests/

# Upload to Codecov (CI)
# Added automatically via GitHub Actions workflow
```

---

## ☸️ Kubernetes Deployment (Helm)

```bash
# Install
helm install fastapi-boilerplate ./helm

# Upgrade
helm upgrade fastapi-boilerplate ./helm
```

**`values.yaml` key settings:**
```yaml
replicaCount: 3
image:
  repository: zyntroai/fastapi-boilerplate
  tag: latest
ingress:
  enabled: true
  hosts: [{ host: fastapi.local, paths: ["/"] }]
resources:
  limits: { cpu: 500m, memory: 512Mi }
```

---

## 📁 Repository Structure

```
fastapi-python-boilerplate/
├── .github/workflows/     # CI/CD pipelines (CI, CodeQL, Release)
├── api/                    # Route definitions
├── app/                    # Core logic, config, security
├── docker/                 # Container configs
├── helm/                   # Kubernetes Helm charts
├── k8s/                    # K8s manifests
├── scripts/                # Utility scripts
├── services/               # Business logic layer
├── tests/                  # Unit & integration tests
├── docker-compose.yml      # Local dev stack
├── requirements.txt         # Python dependencies
└── main.py                  # Application entry point
```

---

## 📜 License

**MIT License** © 2026 ZyntroAI — see [LICENSE](https://github.com/ZyntroAI/fastapi-python-boilerplate/blob/main/LICENSE) for details.

---

## 🧠 Credits

- **FastAPI** — Modern web framework
- **LangGraph** — AI agent orchestration
- **PostgreSQL** — Relational database
- **Docker Compose** — Local development
- **Stripe** — Payments & billing
- **Traefik** — Ingress & reverse proxy
- **Helm** — Kubernetes package manager
- **Twilio / Jira / PagerDuty** — Enterprise alerting

---

✅ **Ready‑to‑paste** — copy this entire README into your repo!  
✅ **All badges fixed** — workflow links point to actual files (`ci.yml`, `codeql.yml`)  
✅ **Complete coverage** — backend, AI, payments, auth, containers, K8s, alerts

Would you like me to also include the **Codecov upload workflow YAML** block so your coverage badge starts working automatically? 📊✅

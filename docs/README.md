```  
# ⚡ FastAPI Python Boilerplate

> Production-ready FastAPI starter template — secure, structured, and batteries-included

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-FF0000.svg)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI Status](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions)

---

## 🚀 Quick Start

```bash
# 1️⃣ Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Setup environment variables
cp .env.example .env
# Edit .env with your values

# 4️⃣ Run development server
uvicorn app.main:app --reload

# ✅ Open: http://127.0.0.1:8000
# 📖 Docs: http://127.0.0.1:8000/docs
 
 
 
 
📋 Features
 
✅ Core
 
- FastAPI — Modern, fast, async-first web framework
- Pydantic v2 — Data validation & settings management
- Uvicorn — Lightning-fast ASGI server
 
🔐 Security
 
- JWT Authentication — Access + Refresh tokens
- Password Hashing — bcrypt via  passlib 
- CORS Configuration — Whitelist allowed origins
- Rate Limiting — Prevent abuse
- Input Sanitization — Automatic validation
 
🗄️ Database
 
- SQLAlchemy 2.0 — Async ORM
- Alembic — Database migrations
- SQLite (dev) → PostgreSQL (prod) — switch easily
 
🧪 Developer Experience
 
- Ruff — Lightning-fast linting & formatting
- Pytest — Full test suite template
- GitHub Actions CI — Lint → Test → Security Scan
- Pre-commit Hooks — Catch issues before commit
- Dockerfile — Production-ready container
- Docker Compose — Local stack with DB & Redis
 
 
 
📁 Project Structure
 
plaintext  
fastapi-python-boilerplate/
├── app/
│   ├── __init__.py
│   ├── main.py              # ✨ Entry point
│   ├── config.py            # ⚙️ Settings & env vars
│   ├── database.py          # 🗄️ DB connection
│   ├── models/              # ORM models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── auth.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   └── dependencies.py # 🔐 Reusable dependencies
│   ├── core/                # Business logic
│   │   ├── __init__.py
│   │   ├── security.py      # JWT, password hashing
│   │   └── exceptions.py    # Custom exceptions
│   └── utils/               # Helpers
├── alembic/                 # 📝 Database migrations
├── tests/                   # 🧪 Unit & Integration tests
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_health.py
├── .env.example             # 🔑 Environment template
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── pytest.ini
├── .pre-commit-config.yaml
├── alembic.ini
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
 src/
├── app/api/
│   └── prompt/route.ts
└── lib/
    ├── api/
    │   ├── http-error.ts
    │   └── response.ts
    ├── validation/
    │   └── prompt.schema.ts
    ├── security/
    │   ├── rate-limit.ts
    │   └── auth.ts
    └── observability/
        └── logger.ts
 
 
 
⚙️ Environment Variables
 
Copy  .env.example  →  .env :
 
env  
# ── Application ─────────────────────────────
APP_NAME=FastAPI Boilerplate
APP_ENV=development          # development | staging | production
APP_VERSION=1.0.0
DEBUG=true

# ── Server ─────────────────────────────────
HOST=0.0.0.0
PORT=8000

# ── Database ───────────────────────────────
DATABASE_URL=sqlite:///./dev.db
# DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# ── Security ────────────────────────────────
SECRET_KEY=change-me-super-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── CORS ────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
 
 
 
 
🧪 Development Commands
 
bash  
# Run dev server (auto-reload)
uvicorn app.main:app --reload --port 8000

# Run with workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Lint & format
ruff check .
ruff format .

# Run tests
pytest -v
pytest --cov=app --cov-report=term-missing

# Database migrations
alembic revision --autogenerate -m "Add users table"
alembic upgrade head

# Docker
docker build -t fastapi-app .
docker run -p 8000:8000 --env-file .env fastapi-app

# Docker Compose (full stack)
docker-compose up -d
 
 
 
 
📖 API Endpoints
 
Health
 
Method Endpoint Description 
GET  /  Service info 
GET  /health  Health check 
GET  /ready  Readiness check 
 
Auth
 
Method Endpoint Description Auth 
POST  /api/v1/auth/register  Register new user — 
POST  /api/v1/auth/login  Login → get tokens — 
POST  /api/v1/auth/refresh  Refresh access token Refresh 🔑 
POST  /api/v1/auth/logout  Logout — 
 
Users
 
Method Endpoint Description Auth 
GET  /api/v1/users/me  Get current user info Access 🔑 
PUT  /api/v1/users/me  Update profile Access 🔑 
GET  /api/v1/users/{id}  Get user by ID Admin 🔑 
 
📮 Full docs:  /docs  (Swagger UI) or  /redoc  (ReDoc)
 
 
 
🐳 Docker Deployment
 
bash  
# Build & run
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Stop & wipe data
docker-compose down -v
 
 
 
 
🤝 Contributing
 
See CONTRIBUTING.md for development guidelines, PR process, and code standards.
 
Quick Contribution Flow
 
1. Fork → Create branch:  feat/your-feature 
2. Make changes → Run tests → Lint
3. Commit:  feat: add amazing feature 
4. Push → Open Pull Request
 
 
 
📋 Roadmap
 
🔐 OAuth2 / Google & GitHub Login
📧 Email verification & password reset
📊 Admin Dashboard
📤 File uploads
🔍 Full-text search
📡 WebSocket support
📱 Admin CLI
 
 
 
📄 License
 
MIT License — Copyright © 2026 ZyntroAI
 
 
 
💡 About
 
Built with ❤️ by ZyntroAI · Production-ready starting point for your next FastAPI project.
 
⭐ Star the repo if you find it useful!
🔗 https://github.com/ZyntroAI/fastapi-python-boilerplate
 
plaintext  

---

✅ คัดลอกทั้งบล็อก → บันทึกเป็น `README.md` ที่รูทโปรเจกต์ได้เลยครับ

ต้องการปรับเปลี่ยนอะไรเพิ่มไหมครับ — เช่น เพิ่ม Badges, เปลี่ยนรายการ Features, หรือปรับ Deployment Instructions? 😊
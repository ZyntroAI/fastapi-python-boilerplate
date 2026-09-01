🐳 Docker Schema — Python Application Complete Stack
 
ครบชุดทั้ง Dockerfile, docker-compose.yml, .env schema, และ Python best practices — พร้อมใช้งานทันที ✅
 
 
 
📋 1. Dockerfile — Python Multi-Stage Build (Recommended)
 
dockerfile
  
# ============================================
# 🐳 Dockerfile — Python Application Schema
# Stage 1: Builder → Install dependencies
# Stage 2: Runtime → Lean production image
# ============================================

# ---------- Builder Stage (Install Dependencies) ----------
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first (caching optimization)
COPY requirements.txt .

# Install Python dependencies to temp directory
RUN pip install --user --no-cache-dir -r requirements.txt

# ---------- Runtime Stage (Lean Production) ----------
FROM python:3.12-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Copy installed packages from builder
COPY --from=builder /root/.local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /root/.local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command (override in docker-compose.yml)
CMD ["python", "main.py"]
 
 
 
 
📋 2. docker-compose.yml — Full Stack Schema
 
yaml
  
# ============================================
# 🐳 Docker Compose — Python Full Stack Schema
# Services: API (FastAPI) + PostgreSQL + Redis + Worker
# ============================================
version: '3.8'

x-common-env: &common-env
  ENVIRONMENT: ${ENVIRONMENT:-development}
  LOG_LEVEL: ${LOG_LEVEL:-INFO}
  TZ: Asia/Bangkok

services:
  # ─────────── Python API Service (FastAPI) ───────────
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: ${BUILD_TARGET:-runtime}
    container_name: ${COMPOSE_PROJECT_NAME:-app}-api
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      <<: *common-env
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASS:-postgres}@postgres:5432/${DB_NAME:-app_db}
      REDIS_URL: redis://${REDIS_HOST:-redis}:6379/0
      SECRET_KEY: ${SECRET_KEY}
    volumes:
      # Development: mount code for hot-reload
      - ./app:/app/app:ro
      # Production: remove volume, use built-in code
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    networks:
      - backend
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

  # ─────────── PostgreSQL Database ───────────
  postgres:
    image: postgres:16-alpine
    container_name: ${COMPOSE_PROJECT_NAME:-app}-postgres
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASS:-postgres}
      POSTGRES_DB: ${DB_NAME:-app_db}
      TZ: Asia/Bangkok
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "${DB_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-app_db}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - backend
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # ─────────── Redis Cache / Queue ───────────
  redis:
    image: redis:7-alpine
    container_name: ${COMPOSE_PROJECT_NAME:-app}-redis
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - backend
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 256M

  # ─────────── Background Worker (Python) ───────────
  worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ${COMPOSE_PROJECT_NAME:-app}-worker
    environment:
      <<: *common-env
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASS:-postgres}@postgres:5432/${DB_NAME:-app_db}
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./app:/app/app:ro
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: ["python", "-m", "rq", "worker", "--url", "redis://redis:6379/0", "default"]
    networks:
      - backend

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
 
 
 
 
📋 3. Environment Variables Schema —  .env 
 
env
  
# ============================================
# 📋 Environment Variables Schema
# Copy to .env and fill in values
# ============================================

# ---------- Project ----------
COMPOSE_PROJECT_NAME=myapp
ENVIRONMENT=development  # development | staging | production
LOG_LEVEL=INFO
TZ=Asia/Bangkok

# ---------- API ----------
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4

# ---------- Database (PostgreSQL) ----------
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASS=SuperSecretPassword
DB_NAME=myapp_db
DATABASE_URL=postgresql://postgres:SuperSecretPassword@postgres:5432/myapp_db

# ---------- Redis ----------
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# ---------- Security ----------
SECRET_KEY=change_this_to_very_long_random_string_32chars_min
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ---------- Docker Build ----------
BUILD_TARGET=runtime  # runtime | builder
 
 
 
 
📋 4. requirements.txt — Python Dependencies Schema
 
txt
  
# ============================================
# 📋 requirements.txt
# Format: package==version  # category
# ============================================

# ---------- Web Framework ----------
fastapi==0.115.0          # Web API framework
uvicorn[standard]==0.32.0 # ASGI server
python-multipart==0.0.12  # File upload support

# ---------- Database ----------
psycopg2-binary==2.9.9    # PostgreSQL adapter
sqlalchemy==2.0.35        # ORM
alembic==1.13.3           # Migrations

# ---------- Cache & Queue ----------
redis==5.2.0              # Redis client
rq==2.0.0                 # Background task queue

# ---------- Validation & Config ----------
pydantic==2.9.2           # Data validation
pydantic-settings==2.6.0  # Env vars management
python-dotenv==1.0.1      # .env file support

# ---------- Security ----------
bcrypt==4.2.0             # Password hashing
pyjwt==2.9.0              # JWT tokens
cryptography==43.0.3       # Encryption utils

# ---------- Utilities ----------
requests==2.32.3          # HTTP client
pydantic-core==2.20.0     # Performance core

# ---------- Development (dev only) ----------
ruff==0.6.0               # Linting & formatting
pytest==8.3.3             # Testing framework
pytest-asyncio==0.24.0    # Async test support
httpx==0.27.2             # Test client
 
 
 
 
📋 5. Python Main Application Template ( main.py )
 
python
  
# ============================================
# 🐍 Python FastAPI Application — Docker Ready
# ============================================
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

# ---------- Configuration ----------
class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# ---------- Logging ----------
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------- Lifespan (Startup/Shutdown) ----------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Startup
    logger.info(f"🚀 Starting app in {settings.environment} mode")
    yield
    # Shutdown
    logger.info("👋 Shutting down gracefully")

# ---------- App Initialization ----------
app = FastAPI(
    title="Python Docker API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url=None,
)

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Health Check (Required for Docker) ----------
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
    }

# ---------- Routes ----------
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Python Docker API 🐳"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.environment == "development",
        workers=1 if settings.environment == "development" else 4,
    )
 
 
 
 
📋 6.  .dockerignore  — Exclude from Build
 
dockerignore
  
# ============================================
# 🚫 .dockerignore — Reduce Image Size
# ============================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
build/
dist/
*.egg-info/
.dockerignore
Dockerfile
.git
.gitignore
.github
*.md
*.log
.pytest_cache/
.coverage
htmlcov/
.env
.env.*
*.db
*.sqlite
.DS_Store
 
 
 
 
✅ Quick Start Commands
 
bash
  
# 1. Copy files to project
#    Dockerfile / docker-compose.yml / .env.example → .env / requirements.txt / main.py

# 2. Build & start all services
docker compose up -d --build

# 3. View logs
docker compose logs -f api

# 4. Check health
curl http://localhost:8000/health

# 5. Stop services
docker compose down

# 6. Stop & remove volumes (reset DB)
docker compose down -v
 
 
 
 
📊 Docker Schema Summary
 
File Purpose Production Ready 
 Dockerfile  Multi-stage build → lean image ✅ Yes 
 docker-compose.yml  Full stack orchestration ✅ Yes 
 .env  Environment config ✅ Yes 
 requirements.txt  Python dependencies ✅ Yes 
 main.py  FastAPI app with health check ✅ Yes 
 .dockerignore  Reduce image size ✅ Yes 
 
 
 
ต้องการปรับแต่งเพิ่มเติมไหมครับ เช่น เพิ่ม Nginx reverse proxy, Traefik, Kubernetes manifests, หรือ GitHub Actions CI/CD สำหรับ build Docker image? 🐳

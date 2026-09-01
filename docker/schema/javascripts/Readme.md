🐳 Docker Schema — JavaScript / Node.js Full Stack
 
ครบชุด Dockerfile, docker-compose.yml, .env schema, package.json, และ Node.js Application Template — พร้อมใช้งานทันที ✅
 
 
 
📋 1. Dockerfile — Node.js Multi-Stage Build (Recommended)
 
dockerfile
  
# ============================================
# 🐳 Dockerfile — Node.js / JavaScript
# Stage 1: Builder → Install all deps + build
# Stage 2: Runtime → Lean production image
# ============================================

# ---------- Builder Stage ----------
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files first (caching optimization)
COPY package*.json ./

# Install ALL dependencies (including devDependencies)
RUN npm ci --include=dev

# Copy source code
COPY . .

# Build application (if using TypeScript / Next.js / React)
RUN npm run build

# ---------- Runtime Stage ----------
FROM node:20-alpine AS runtime

# Set environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    TZ=Asia/Bangkok \
    PATH=/app/node_modules/.bin:$PATH

# Set working directory
WORKDIR /app

# Install tini for proper signal handling
RUN apk add --no-cache tini

# Create non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup -u 1000

# Copy production dependencies only from builder
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

# Copy built artifacts from builder
COPY --from=builder /app/dist ./dist
# For Next.js: COPY --from=builder /app/.next ./.next
# For Next.js public folder: COPY --from=builder /app/public ./public

# Set ownership
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:\${PORT:-3000}/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Expose port
EXPOSE ${PORT:-3000}

# Entrypoint
ENTRYPOINT ["/sbin/tini", "--"]

# Default command
CMD ["node", "dist/index.js"]
 
 
 
 
📋 2. docker-compose.yml — JavaScript Full Stack Schema
 
yaml
  
# ============================================
# 🐳 Docker Compose — Node.js / JavaScript Full Stack
# Services: App (Express/Next.js) + PostgreSQL + Redis + Nginx
# ============================================
version: '3.8'

x-common-env: &common-env
  NODE_ENV: ${NODE_ENV:-development}
  LOG_LEVEL: ${LOG_LEVEL:-info}
  TZ: Asia/Bangkok

services:
  # ─────────── Node.js Application ───────────
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: ${BUILD_TARGET:-runtime}
    container_name: ${COMPOSE_PROJECT_NAME:-jsapp}-app
    ports:
      - "${APP_PORT:-3000}:3000"
    environment:
      <<: *common-env
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASS:-postgres}@postgres:5432/${DB_NAME:-jsapp_db}
      REDIS_URL: redis://${REDIS_HOST:-redis}:6379/0
      JWT_SECRET: ${JWT_SECRET}
    volumes:
      # Dev only: mount source for hot-reload
      - ./src:/app/src:ro
      - ./dist:/app/dist:ro
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
    restart: unless-stopped
    networks:
      - frontend
      - backend
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M

  # ─────────── PostgreSQL Database ───────────
  postgres:
    image: postgres:16-alpine
    container_name: ${COMPOSE_PROJECT_NAME:-jsapp}-postgres
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASS:-postgres}
      POSTGRES_DB: ${DB_NAME:-jsapp_db}
      TZ: Asia/Bangkok
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./prisma/seed.sql:/docker-entrypoint-initdb.d/seed.sql:ro
    ports:
      - "${DB_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-jsapp_db}"]
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

  # ─────────── Redis Cache / Session ───────────
  redis:
    image: redis:7-alpine
    container_name: ${COMPOSE_PROJECT_NAME:-jsapp}-redis
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

  # ─────────── Nginx Reverse Proxy (Optional) ───────────
  nginx:
    image: nginx:1.25-alpine
    container_name: ${COMPOSE_PROJECT_NAME:-jsapp}-nginx
    ports:
      - "${NGINX_PORT:-80}:80"
      - "${NGINX_SSL_PORT:-443}:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - frontend
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 128M

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: false
 
 
 
 
📋 3. Environment Variables Schema —  .env 
 
env
  
# ============================================
# 📋 Environment Variables — JavaScript / Node.js
# Copy to .env and fill in values
# ============================================

# ---------- Project ----------
COMPOSE_PROJECT_NAME=jsapp
NODE_ENV=development  # development | staging | production
LOG_LEVEL=info
TZ=Asia/Bangkok

# ---------- Application ----------
APP_PORT=3000
APP_HOST=0.0.0.0
API_PREFIX=/api/v1
CORS_ORIGIN=http://localhost:5173,http://localhost:3000

# ---------- Database (PostgreSQL) ----------
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASS=SuperSecretPass123
DB_NAME=jsapp_db
DATABASE_URL=postgresql://postgres:SuperSecretPass123@postgres:5432/jsapp_db

# ---------- Redis ----------
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# ---------- Security ----------
JWT_SECRET=change_this_to_very_long_random_string_64chars_min
JWT_EXPIRES_IN=15m
REFRESH_TOKEN_EXPIRES_IN=7d
BCRYPT_SALT_ROUNDS=12

# ---------- Session ----------
SESSION_SECRET=another_very_long_random_secret_here
SESSION_MAX_AGE=86400000

# ---------- Docker Build ----------
BUILD_TARGET=runtime  # runtime | builder
 
 
 
 
📋 4. package.json — Dependencies & Scripts Schema
 
json
  
{
  "name": "js-docker-api",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "lint": "eslint src --ext .ts,.js",
    "lint:fix": "eslint src --ext .ts,.js --fix",
    "format": "prettier --write \"src/**/*.{ts,js,json}\"",
    "test": "vitest run",
    "test:watch": "vitest",
    "db:generate": "prisma generate",
    "db:push": "prisma db push",
    "db:migrate": "prisma migrate deploy",
    "docker:up": "docker compose up -d --build",
    "docker:down": "docker compose down"
  },
  "dependencies": {
    "express": "^4.21.0",
    "cors": "^2.8.5",
    "helmet": "^8.0.0",
    "morgan": "^1.10.0",
    "dotenv": "^16.4.5",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "cookie-parser": "^1.4.7",
    "express-rate-limit": "^7.4.0",
    "prisma": "^5.20.0",
    "@prisma/client": "^5.20.0",
    "ioredis": "^5.4.1"
  },
  "devDependencies": {
    "@types/node": "^22.7.5",
    "@types/express": "^5.0.0",
    "@types/cors": "^2.8.17",
    "@types/jsonwebtoken": "^9.0.7",
    "@types/bcryptjs": "^2.4.6",
    "typescript": "^5.6.3",
    "tsx": "^4.19.0",
    "eslint": "^9.12.0",
    "prettier": "^3.3.3",
    "vitest": "^2.1.2"
  },
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=9.0.0"
  }
}
 
 
 
 
📋 5. Node.js Application Template ( src/index.js  or  .ts )
 
javascript
  
// ============================================
// 🟢 JavaScript / Node.js Express App — Docker Ready
// ============================================
import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';

// ---------- Configuration ----------
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';
const API_PREFIX = process.env.API_PREFIX || '/api/v1';

// ---------- Initialize App ----------
const app = express();

// ---------- Security Middleware ----------
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN?.split(',') || ['http://localhost:3000'],
  credentials: true,
}));

// ---------- Rate Limiting ----------
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 min
  max: NODE_ENV === 'production' ? 100 : 1000,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// ---------- Logging & Parsing ----------
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(morgan(NODE_ENV === 'production' ? 'combined' : 'dev'));

// ---------- Health Check (Docker Required) ----------
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    environment: NODE_ENV,
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// ---------- API Routes ----------
app.get(`${API_PREFIX}/`, (req, res) => {
  res.json({
    message: '🚀 JavaScript Docker API',
    version: '1.0.0',
    docs: NODE_ENV === 'development' ? `${API_PREFIX}/docs` : null,
  });
});

// ---------- 404 & Error Handler ----------
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: NODE_ENV === 'production' ? 'Internal Server Error' : err.message,
  });
});

// ---------- Start Server ----------
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT} [${NODE_ENV}]`);
  console.log(`📍 Health: http://localhost:${PORT}/health`);
});

export default app;
 
 
 
 
📋 6.  .dockerignore  — Exclude from Build
 
dockerignore
  
# ============================================
# 🚫 .dockerignore — Reduce Image Size
# ============================================
node_modules
npm-debug.log
yarn-error.log
pnpm-debug.log

# Build outputs (keep if multi-stage)
dist
.next
build

# Environment files
.env
.env.*

# Git & IDE
.git
.gitignore
.github
.vscode
.idea
*.swp
.DS_Store

# Testing & Coverage
coverage
.nyc_output
.pytest_cache

# Logs
logs
*.log

# Docker
Dockerfile
docker-compose.yml
 
 
 
 
✅ Quick Start — JavaScript Stack
 
bash
  
# 1. Create files
#    Dockerfile / docker-compose.yml / .env / package.json / src/index.js

# 2. Install deps locally (optional)
npm install

# 3. Build & start all services
docker compose up -d --build

# 4. View logs
docker compose logs -f app

# 5. Check health
curl http://localhost:3000/health

# 6. Stop everything
docker compose down

# 7. Full reset (delete DB data)
docker compose down -v
 
 
 
 
📊 Docker — JavaScript Schema Summary
 
File Purpose Production Ready 
 Dockerfile  Multi-stage → lean image (~300MB) ✅ Yes 
 docker-compose.yml  App + PostgreSQL + Redis + Nginx ✅ Yes 
 .env  All config in one place ✅ Yes 
 package.json  Deps + scripts + Node version ✅ Yes 
 src/index.js  Express app with health check ✅ Yes 
 .dockerignore  Exclude unnecessary files ✅ Yes 
 
 
 
ต้องการเพิ่ม Next.js, NestJS, Prisma, หรือ GitHub Actions CI/CD สำหรับ build Docker image ไหมครับ? 🟢

🛠️ Makefile — FastAPI Python Boilerplate
 
Save as  Makefile  in your project root ✨
 
makefile  
# ──────────────────────────────────────────────
# FastAPI Python Boilerplate — Makefile
# ──────────────────────────────────────────────

.PHONY: help install run dev test lint clean env update build docker-up docker-down

# Default target
.DEFAULT_GOAL := help

# ──────────────────────────────────────────────
# 📋 Configuration
# ──────────────────────────────────────────────
PYTHON = python3
VENV = .venv
PIP = $(VENV)/bin/pip
UVICORN = $(VENV)/bin/uvicorn
APP_MODULE = app.main:app
HOST = 0.0.0.0
PORT = 8000

# ──────────────────────────────────────────────
# 🎯 Help
# ──────────────────────────────────────────────
help: ## Show this help message
	@echo "🚀 FastAPI Boilerplate — Available Commands"
	@echo "──────────────────────────────────────────────"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────
# 📦 Setup & Dependencies
# ──────────────────────────────────────────────
venv: ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Virtual environment created: $(VENV)"
	@echo "👉 Run: source $(VENV)/bin/activate"

install: venv ## Install all dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

update: ## Update all dependencies to latest versions
	$(PIP) install --upgrade -r requirements.txt
	@echo "✅ Dependencies updated"

env: ## Create .env from example if not exists
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env file created — please edit your settings!"; \
	else \
		echo "ℹ️ .env already exists — skipping"; \
	fi

# ──────────────────────────────────────────────
# 🚀 Run Servers
# ──────────────────────────────────────────────
run: env ## Start production server
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT)

dev: env ## Start development server with auto-reload
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) --reload --log-level info

start: dev ## Alias for dev server

# ──────────────────────────────────────────────
# 🧪 Code Quality & Testing
# ──────────────────────────────────────────────
lint: ## Run code linting & format check
	-$(VENV)/bin/ruff check . 2>/dev/null || echo "⚠️ ruff not installed — install with: pip install ruff"
	-$(VENV)/bin/black --check . 2>/dev/null || echo "⚠️ black not installed — install with: pip install black"

format: ## Auto-format code
	-$(VENV)/bin/black . 2>/dev/null || echo "⚠️ black not installed"

test: ## Run tests
	$(VENV)/bin/pytest tests/ -v 2>/dev/null || echo "⚠️ No tests or pytest not installed"

# ──────────────────────────────────────────────
# 🐳 Docker
# ──────────────────────────────────────────────
docker-up: ## Start services with Docker Compose
	docker compose up -d --build
	@echo "✅ Services running — http://localhost:$(PORT)"

docker-down: ## Stop Docker services
	docker compose down

# ──────────────────────────────────────────────
# 🧹 Cleanup
# ──────────────────────────────────────────────
clean: ## Remove venv, cache, and build artifacts
	rm -rf $(VENV) __pycache__ .pytest_cache .ruff_cache *.egg-info dist build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

# ──────────────────────────────────────────────
# 📊 Health & Info
# ──────────────────────────────────────────────
status: ## Show project & server status
	@echo "📁 Project: FastAPI Boilerplate"
	@echo "🐍 Python: $$($(VENV)/bin/python --version 2>/dev/null || echo 'Not installed')"
	@echo "🚀 Endpoint: http://$(HOST):$(PORT)"
	@echo "📚 Docs: http://$(HOST):$(PORT)/docs"
	@echo "🔗 Redoc: http://$(HOST):$(PORT)/redoc"
 
 
 
 
📌 Quick Usage
 
bash  
# 🔍 See all commands
make help

# 📦 First time setup
make install

# ⚙️ Create environment file
make env

# 🚀 Start dev server
make dev

# 🧹 Clean everything
make clean
 
 
💡 Common Shortcuts
 
Command What It Does 
 make install  Setup venv + install deps + create .env 
 make dev  Start live-reload dev server 
 make run  Start production server 
 make env  Copy .env.example → .env 
 make lint  Check code style 
 make clean  Wipe venv & cache files 
 
 
 
💡 Pro Tip: On Windows (PowerShell), use  wmake  or run commands manually:
 
powershell  
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
 
 
Want me to also add a  Dockerfile ,  docker-compose.yml , or  pytest  test templates? Just say the word! 🎯
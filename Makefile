# ============================================================
# FastAPI Python Boilerplate — Dev Workflow Makefile
# Adapted from the automated dev-workflow gist for this repo.
#
# Backend: FastAPI (OAuth2 PKCE) + pytest + ruff + uvicorn
# Layout:  app/ (package), tests/ (suite), pytest/requirements.txt
# ============================================================

# --- Configuration -------------------------------------------------------
PY     ?= python3
VENV   ?= .venv
PY_BIN  = $(VENV)/bin
REQ    ?= pytest/requirements.txt   # this repo keeps deps here
ENV    ?= local

.PHONY: help setup install test lint format check run clean

help:
	@echo "FastAPI Python Boilerplate workflow commands:"
	@echo ""
	@echo "  make setup   - create venv and install deps from $(REQ)"
	@echo "  make install - install/refresh deps from $(REQ)"
	@echo "  make test    - run the pytest suite (tests/)"
	@echo "  make lint    - ruff check (app tests)"
	@echo "  make format  - ruff format (app tests)"
	@echo "  make check   - full pre-PR gate: format + lint + test"
	@echo "  make run     - uvicorn dev server on :8000 (ENV=$(ENV))"
	@echo "  make clean   - remove venv and caches"

setup:
	$(PY) -m venv $(VENV)
	$(PY_BIN)/pip install --upgrade pip setuptools wheel
	$(PY_BIN)/pip install -r $(REQ)
	$(PY_BIN)/pip install ruff pytest-cov pre-commit

install:
	$(PY_BIN)/pip install -r $(REQ)

test:
	$(PY_BIN)/python -m pytest tests/ -q

lint:
	$(PY_BIN)/ruff check app tests

format:
	$(PY_BIN)/ruff format app tests

check: format lint test
	@echo "All FastAPI boilerplate checks passed."

run:
	$(PY_BIN)/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

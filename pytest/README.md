# 📄 README.md — Pytest Testing Guide (Ready to Paste)

```markdown
# 🧪 Testing Guide — Pytest

FastAPI Python Boilerplate uses **pytest** for full test automation: unit tests, integration tests, async support, and coverage reporting.

---

## ✅ Quick Start

### Install Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov httpx
# or
poetry install --with dev
```

### Run All Tests
```bash
pytest -v
```

### Run with Coverage Report
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

---

## 📁 Test File Structure
```
tests/
├── conftest.py              # Shared fixtures, fixtures, async setup
├── test_*.py                # Unit tests per module
├── api/                     # API route tests
│   └── test_*.py
└── integration/             # End-to-end / integration tests
    └── test_*.py
```

---

## ⚙️ pytest Configuration — `pyproject.toml`
```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "-v --strict-markers"

markers = [
    "unit: Unit tests (fast, no external resources)",
    "integration: Integration tests (may use DB/services)",
    "slow: Slow tests — skip by default",
    "auth: Authentication/authorization tests",
]
```

---

## 🧪 Common Commands Cheatsheet

| Command | What It Does |
|---|---|
| `pytest -v` | Run all tests verbose |
| `pytest tests/api/ -v` | Run only API tests |
| `pytest -k "create or get" -v` | Run tests matching keyword |
| `pytest -m "not slow" -v` | Skip slow tests |
| `pytest --tb=short` | Shorter tracebacks |
| `pytest --cov=app` | Show coverage |
| `pytest --cov=app --cov-report=html` | Generate HTML report → open `htmlcov/index.html` |

---

## 🔄 Async Test Example
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## ✅ CI Integration
Tests run automatically on every PR/push via GitHub Actions:
```yaml
# .github/workflows/tests.yml
- name: Run Tests
  run: |
    pytest -v --cov=app --cov-report=term-missing
```

---

## 📋 Best Practices
- ✅ Test files: `test_*.py`
- ✅ Test functions: `test_*`
- ✅ Mark slow tests: `@pytest.mark.slow`
- ✅ Keep unit tests fast → no external calls
- ✅ Coverage ≥ 80% required before merge
```

---

## 🚀 Ready to Use
**Copy → Save as `README.md` (or `docs/testing-pytest.md`) → Commit!**

Want me to also generate the actual **`tests/conftest.py`** and **example test files** so you can run `pytest` immediately? 🧪✅

นี่คือเวอร์ชัน **Python script** ที่จะสร้าง workflow CI/CD ของคุณ (แทน YAML) โดยใช้ `PyYAML` — คุณสามารถรันสคริปต์นี้เพื่อพิมพ์ไฟล์ `.github/workflows/ci.yml` ออกมาได้:

---

## 📄 `generate_ci.py`

```python
import yaml

workflow = {
    "name": "FastAPI CI/CD",
    "on": {
        "push": {"branches": ["main", "dev"]},
        "pull_request": {"branches": ["main"]},
    },
    "env": {
        "PYTHON_VERSION": "3.12",
        "IMAGE_NAME": "ghcr.io/zyntroai/fastapi-boilerplate",
        "REGISTRY": "ghcr.io",
    },
    "jobs": {
        "lint": {
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@f548e57c3d3c42e288026812cd22362661c4e8d4"},
                {
                    "uses": "actions/setup-python@5fda3b9c709277f8cf4290f3a0094ab7e95c1338",
                    "with": {"python-version": "${{ env.PYTHON_VERSION }}"},
                },
                {"run": "python -m pip install ruff black isort"},
                {"run": "ruff check ."},
                {"run": "black --check ."},
            ],
        },
        "test": {
            "needs": "lint",
            "runs-on": "ubuntu-latest",
            "services": {
                "postgres": {
                    "image": "postgres:16-alpine",
                    "env": {
                        "POSTGRES_USER": "test",
                        "POSTGRES_PASSWORD": "test",
                        "POSTGRES_DB": "test",
                    },
                    "ports": ["5432:5432"],
                    "options": "--health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5",
                }
            },
            "steps": [
                {"uses": "actions/checkout@f548e57c3d3c42e288026812cd22362661c4e8d4"},
                {
                    "uses": "actions/setup-python@5fda3b9c709277f8cf4290f3a0094ab7e95c1338",
                    "with": {"python-version": "${{ env.PYTHON_VERSION }}"},
                },
                {"run": "pip install -r requirements.txt"},
                {
                    "name": "Run Tests with Coverage",
                    "run": "pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=xml",
                    "env": {"DATABASE_URL": "postgresql://test:test@localhost:5432/test"},
                },
                {
                    "name": "Upload Coverage to Codecov",
                    "uses": "codecov/codecov-action@<sha>",
                    "with": {
                        "files": "./coverage.xml",
                        "flags": "unittests",
                        "name": "codecov-coverage",
                        "fail_ci_if_error": False,
                        "verbose": True,
                    },
                },
            ],
        },
        "security": {
            "needs": "test",
            "runs-on": "ubuntu-latest",
            "permissions": {
                "actions": "read",
                "contents": "read",
                "security-events": "write",
            },
            "steps": [
                {
                    "uses": "actions/checkout@f548e57c3d3c42e288026812cd22362661c4e8d4",
                    "with": {"fetch-depth": 2},
                },
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@5fda3b9c709277f8cf4290f3a0094ab7e95c1338",
                    "with": {"python-version": "${{ env.PYTHON_VERSION }}"},
                },
                {"run": "python -m pip install --upgrade pip && pip install -r requirements.txt"},
                {
                    "name": "Initialize CodeQL",
                    "uses": "github/codeql-action/init@977e6ce40888f41234c9b3252437dcf2331daaa2",
                    "with": {"languages": "python", "build-mode": "none"},
                },
                {"name": "Autobuild", "uses": "github/codeql-action/autobuild@977e6ce40888f41234c9b3252437dcf2331daaa2"},
                {
                    "name": "Perform CodeQL Analysis",
                    "uses": "github/codeql-action/analyze@977e6ce40888f41234c9b3252437dcf2331daaa2",
                    "with": {"category": "/language:python"},
                },
            ],
        },
        "build": {
            "needs": "security",
            "runs-on": "ubuntu-latest",
            "if": "github.ref == 'refs/heads/main'",
            "permissions": {"contents": "read", "packages": "write"},
            "steps": [
                {"uses": "actions/checkout@f548e57c3d3c42e288026812cd22362661c4e8d4"},
                {
                    "name": "Log in to GHCR",
                    "uses": "docker/login-action@<sha>",
                    "with": {
                        "registry": "${{ env.REGISTRY }}",
                        "username": "${{ github.actor }}",
                        "password": "${{ secrets.GITHUB_TOKEN }}",
                    },
                },
                {
                    "name": "Build & Push",
                    "uses": "docker/build-push-action@<sha>",
                    "with": {"context": ".", "push": True, "tags": "${{ env.IMAGE_NAME }}:latest"},
                },
            ],
        },
    },
}

if __name__ == "__main__":
    print(yaml.dump(workflow, sort_keys=False))
```

---

## 🚀 วิธีใช้
1. ติดตั้ง `PyYAML`:  
   ```bash
   pip install pyyaml
   ```
2. รันสคริปต์:  
   ```bash
   python generate_ci.py > .github/workflows/ci.yml
   ```
3. แทนที่ `<sha>` ด้วย commit SHA ล่าสุดของ **Codecov**, **docker/login-action**, และ **docker/build-push-action**.

---

คุณอยากให้ผมดึง **commit SHA ล่าสุดของ Codecov และ Docker actions** ให้เลยตอนนี้ เพื่อแทน `<sha>` โดยตรงในสคริปต์นี้ไหม?

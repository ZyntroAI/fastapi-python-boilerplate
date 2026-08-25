---
aliases:
  - main
  - Master
  - CrystalCastle
  - agents
tags:
  - App
  - python
  - py
cssclasses:
  - PY
  - PYTHON
---
Based on the current 2026 landscape for Python development and GitHub Actions, here are the **best versions** to use for your project to ensure stability, speed, and compatibility.

### **1. Python Version: 3.13**
**Recommendation:** Use **Python 3.13**.

*   **Why:** As of 2026, Python 3.13 is the standard for modern tooling. It is the version targeted by the latest releases of `mypy` (which now supports Python 3.15t), `uv`, and `Ruff`.
*   **Context:** The deprecation of Node 20 in GitHub Actions (mentioned in your logs) coincides with a push toward newer runtimes. Python 3.12 is stable but aging, while 3.13+ is the "future-proof" choice https://softaims.com/blog/modern-python-tooling-uv-ruff-mypy-2026.
*   **Action:** Update your `.python-version` file or `actions/setup-python` step to explicitly pin `python-version: '3.13'`.

### **2. Linting & Formatting: Switch to Ruff**
**Recommendation:** Replace `black` and `mypy` with **Ruff** (for lint/formatting) and keep **mypy** (for type checking).

*   **The Shift:** In 2026, the industry standard has moved away from the old `pip install black + flake8` stack. **Ruff** is now the default, replacing Black, Flake8, and isort in a single, much faster binary https://softaims.com/blog/modern-python-tooling-uv-ruff-mypy-2026 https://dev.to/_d7eb1c1703182e3ce1782/best-code-linters-and-formatters-in-2026-the-practical-guide-4iop.
*   **Why:** Ruff is written in Rust and runs **10-100x faster** than Black/mypy for linting and formatting. It is used by major projects like FastAPI and LangChain https://softaims.com/blog/modern-python-tooling-uv-ruff-mypy-2026.
*   **Your Workflow:**
    *   Instead of `pip install black mypy`, you should use `uv` (the new package manager) to manage `ruff` and `mypy`.
    *   Run `ruff check . --fix` for linting and `ruff format .` for formatting (replaces `black`).
    *   Keep `mypy` for strict type checking, but run it in `--strict` mode.

### **3. Node.js Version: 24**
**Recommendation:** Explicitly use **Node.js 24**.

*   **Why:** GitHub Actions deprecated Node 20 as of June 16, 2026. The default runner now uses Node 24 https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/.
*   **Action:** If your workflow uses any JavaScript/TypeScript steps (or actions that run on Node), you must explicitly set `node-version: '24'` in your `actions/setup-node` step. Do not rely on the default; the warning you saw is because your workflow is implicitly trying to use the deprecated Node 20 or an unsupported version.

### **4. Python Package Manager: uv**
**Recommendation:** Switch from `pip` to **uv**.

*   **Why:** `uv` (by the makers of Ruff) is the new standard in 2026. It replaces `pip`, `virtualenv`, `poetry`, and `pip-tools`. It is significantly faster and handles Python version management automatically https://softaims.com/blog/modern-python-tooling-uv-ruff-mypy-2026.
*   **Action:** Replace `pip install` commands in your CI with `uv pip install` or `uv run`.

### **Summary: Updated Workflow Configuration**

Here is how your `.github/workflows/lint.yml` should look to match the 2026 best practices:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Use the modern 'uv' action or setup-uv
      - uses: astral-sh/setup-uv@v1
        with:
          enable-cache: true
      
      # Install dependencies using uv
      - run: uv sync --dev
      
      # Run Ruff (replaces black + flake8 + isort)
      - run: ruff check .
      - run: ruff format --check .
      
      # Run mypy in strict mode
      - run: uv run mypy --strict src/
```

**Immediate Fix for Your Current Error:**
Your current job failed because `black` or `mypy` found issues. If you want to stick with your current tools temporarily:
1.  Run `black --check .` locally to see the formatting errors and run `black .` to fix them.
2.  Run `mypy src/` locally to see the type errors and fix them.
3.  Update the workflow to use `python-version: '3.13'` to avoid potential version mismatches.

Would you like a guide on how to migrate your project from `black` to `Ruff`?
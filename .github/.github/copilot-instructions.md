# Repository Analysis & Help Instructions

## 🎯 Purpose
These instructions tell GitHub Copilot how to analyze, understand, and assist with this repository as a whole.

---

## 📦 Repository Overview — First Steps
When asked for help or starting a new session, **always perform a full repository scan first**:

### 1. Read Documentation
- Read and summarize: `README.md`, `CONTRIBUTING.md`, `CHANGELOG`, `docs/` folder
- Understand the project's purpose, architecture, and intended audience

### 2. Map the Structure
- List top-level directories and explain what each contains
- Identify: source code, tests, configs, workflows, scripts, assets
- Note the main entry points and how components connect

### 3. Identify Tech Stack
- Languages used → Python, Markdown, YAML, etc.
- Tools & dependencies → Check `pyproject.toml`, `requirements.txt`, `package.json`
- CI/CD → Scan `.github/workflows/`
- Linting/formatting → Ruff, markdownlint, etc.

### 4. Key Files Inventory
- **Scripts:** `commands.py` and any utility scripts
- **Configs:** `.gitignore`, `.ruff.toml`, `.markdownlint.jsonc`
- **Workflows:** `.github/workflows/*.yml`
- **Templates:** Any note/project templates
- **Documentation:** All `.md` files explaining usage

### 5. Health Check
- Search for markers: `TODO`, `FIXME`, `HACK`, `XXX`
- Check for inconsistent naming patterns
- Identify unused files or dead links
- Note any missing documentation

---

## 🔍 How to Answer — General Principles

### ✅ When asked "How do I...?"
1. First search for existing documentation or scripts
2. Show the exact file + line reference
3. Provide copy-pasteable commands/examples
4. Explain what each part does — don't just give code

### ✅ When asked to "Check the repo" or "Status"
Structure your response like this:

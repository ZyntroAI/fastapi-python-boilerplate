Here is a complete setup using Multi’s file-based specification format for defining reusable **Skills** and specialized **Subagents**.

Place these files inside your repository's directory structure to automate testing and verification workflows across both backend and frontend environments.

---

### Directory Layout

```text
.agent/
├── skills/
│   ├── run-backend-tests/
│   │   └── SKILL.md
│   └── run-frontend-check/
│       └── SKILL.md
└── agents/
    ├── backend-qa.md
    └── frontend-qa.md

```

---

### 1. Skill Definitions (`.agent/skills/`)

Skills define repeatable, step-by-step tool workflows that can be invoked by main agents or delegated subagents.

#### Backend Skill: `run-backend-tests`

`path: .agent/skills/run-backend-tests/SKILL.md`

```markdown
---
name: run-backend-tests
description: Run Ruff linting, Mypy type checking, and Pytest test suite for the FastAPI backend.
---

# Run FastAPI Backend Quality Checks

Follow these exact steps to verify the FastAPI backend:

1. **Navigate to Backend Directory:**
   ```bash
   cd backend

```

2. **Run Ruff Linter & Formatter Check:**
```bash
ruff check .
ruff format --check .

```


3. **Run Mypy Type Checker:**
```bash
mypy app

```


4. **Run Pytest Suite:**
* Execute tests with coverage summary:
```bash
pytest -v --tb=short

```




5. **Reporting:**
* If any step fails, inspect tracebacks and identify failing tests or type errors.
* Summarize passing/failing status and outline explicit fixes required.



```

---

#### Frontend Skill: `run-frontend-check`
`path: .agent/skills/run-frontend-check/SKILL.md`

```markdown
---
name: run-frontend-check
description: Run ESLint, TypeScript compiler type checking, and Vitest for the React frontend.
---

# Run React Frontend Quality Checks

Follow these exact steps to verify the React frontend:

1. **Navigate to Frontend Directory:**
   ```bash
   cd frontend

```

2. **Run TypeScript Compiler Check:**
```bash
pnpm typecheck

```


3. **Run ESLint Validation:**
```bash
pnpm lint

```


4. **Run Unit Tests (Vitest):**
```bash
pnpm test --run

```


5. **Reporting:**
* If type checking or linting fails, output exact file names and line numbers with errors.
* Highlight any broken imports, invalid prop types, or failing assertions.



```

---

### 2. Subagent Configurations (`.agent/agents/`)

Subagents run in isolated context windows with scoped tools and instructions to handle heavy verification workloads without diluting the primary agent's context.

#### Backend QA Agent: `backend-qa.md`
`path: .agent/agents/backend-qa.md`

```markdown
---
name: backend-qa
description: Dedicated QA agent for inspecting FastAPI endpoints, running pytest suites, and fixing backend type errors.
tools:
  - bash
  - glob
  - read_file
  - write_file
  - edit_file
---

# Role & Context
You are a specialized FastAPI QA and testing subagent. Your sole focus is ensuring backend stability, type safety, and unit test pass rates.

## Scope & Workflow
- Operate exclusively within the `/backend` directory.
- Use the `run-backend-tests` skill to evaluate the current codebase state.
- When tests fail:
  1. Locate the failing endpoint or service in `app/api/` or `app/services/`.
  2. Write targeted fixes while adhering to SQLModel / Pydantic v2 schemas.
  3. Re-run `pytest` to ensure all tests pass cleanly.
- Never edit frontend files or database schema migrations unless explicitly instructed.

```

---

#### Frontend QA Agent: `frontend-qa.md`

`path: .agent/agents/frontend-qa.md`

```markdown
---
name: frontend-qa
description: Dedicated QA agent for verifying TypeScript types, lint rules, and React component tests.
tools:
  - bash
  - glob
  - read_file
  - write_file
  - edit_file
---

# Role & Context
You are a specialized React & TypeScript QA subagent. Your sole focus is ensuring frontend type safety, component prop compliance, and test suite execution.

## Scope & Workflow
- Operate exclusively within the `/frontend` directory.
- Use the `run-frontend-check` skill to execute `pnpm typecheck`, `pnpm lint`, and `pnpm test`.
- When type errors or lint warnings occur:
  1. Inspect component interfaces and TanStack Query / custom hook definitions.
  2. Fix missing prop definitions or invalid Zod schema inferences.
  3. Verify clean execution of `pnpm typecheck`.
- Do not modify backend API routes or database models.

```

---

### 3. Triggering in Multi

Once placed in your workspace, you can invoke these skills and subagents directly inside Multi:

* **Skill Execution:** `/run-backend-tests` or `/run-frontend-check`
* **Agent Delegation:** Ask Multi: *"Delegate to backend-qa to fix failing pytest cases"* or *"Delegate to frontend-qa to resolve pnpm typecheck errors."*

* Great — here’s the **complete production-ready package**: helper script, extended MCP servers, `.env` template, `.gitignore`, and client config formats for VS Code / Cursor / Claude Desktop.

---

## 📁 Project Structure
```
your-project/
├── .env.mcp                # ← Copy to .env & fill values
├── .gitignore              # ← Updated
├── mcp-config.json          # ← Final enhanced config
├── setup-mcp.sh            # ← Linux/macOS helper
├── setup-mcp.ps1           # ← Windows helper
└── data/                   # ← Auto-created for SQLite
```

---

## 🔐 `.env.mcp` — Environment Template
Save as `.env.mcp`, copy to `.env`, fill in your values:
```env
# ─── MCP Server Configuration ──────────────────────────────
# Rename this file to .env and fill in your values
# Add .env to .gitignore — NEVER commit real tokens!

# GitHub — fine-grained PAT recommended
GITHUB_TOKEN=ghp_yourFineGrainedTokenHere

# Brave Search — get from: https://api.search.brave.com/register
BRAVE_API_KEY=BSAN_yourBraveKeyHere

# Optional: Path overrides (absolute paths recommended)
WORKSPACE_ROOT=${PWD}
DB_PATH=${WORKSPACE_ROOT}/data/app.db
```

---

## 🚀 `mcp-config.json` — Full Production Config
```json
{
  "_comment": "MCP Server Configuration — ZyntroAI Stack",
  "_version": "1.0.0",
  "_docs": "See .env for tokens; run setup script to validate paths",

  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "--no-update-notifier",
        "@modelcontextprotocol/server-filesystem@0.6.0",
        "${workspace}/src",
        "${workspace}/docs",
        "${workspace}/config",
        "${workspace}/scripts"
      ],
      "env": {
        "NODE_ENV": "production"
      },
      "timeout": 30000
    },

    "github": {
      "command": "npx",
      "args": [
        "-y",
        "--no-update-notifier",
        "@modelcontextprotocol/server-github@0.6.0"
      ],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "NODE_ENV": "production"
      },
      "timeout": 30000
    },

    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "--no-update-notifier",
        "@modelcontextprotocol/server-sqlite@0.5.0",
        "${workspace}/data/app.db"
      ],
      "env": {
        "NODE_ENV": "production"
      },
      "timeout": 30000
    },

    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "--no-update-notifier",
        "@modelcontextprotocol/server-brave-search@0.6.0"
      ],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}",
        "NODE_ENV": "production"
      },
      "timeout": 15000
    },

    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "--no-update-notifier",
        "@modelcontextprotocol/server-memory@0.6.0"
      ],
      "env": {
        "NODE_ENV": "production"
      },
      "timeout": 30000
    },

    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "--no-update-notifier",
        "@modelcontextprotocol/server-postgres@0.5.0",
        "postgresql://${DB_USER}:${DB_PASS}@localhost:5432/zyntro_db"
      ],
      "enabled": false,
      "timeout": 30000
    }
  }
}
```

---

## 🛠️ Setup Scripts

### `setup-mcp.sh` — Linux / macOS
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Setting up MCP Environment..."

# 1. Load env
if [ ! -f .env ]; then
    cp .env.mcp .env
    echo "✅ Created .env from template — please edit with your tokens"
fi
set -a; source .env; set +a

# 2. Create directories
mkdir -p data src docs config scripts
echo "✅ Directory structure ready"

# 3. Validate tokens
if [[ "$GITHUB_TOKEN" == "ghp_yourFineGrainedTokenHere" ]]; then
    echo "⚠️  Update GITHUB_TOKEN in .env before using GitHub server"
fi

# 4. Verify npx
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found — install Node.js 20+: https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js/npx available"

echo ""
echo "🎉 Setup complete!"
echo "📁 Config: $(pwd)/mcp-config.json"
echo "📝 Edit .env → then add config to your MCP client"
```

### `setup-mcp.ps1` — Windows PowerShell
```powershell
<#
.SYNOPSIS
Setup MCP Environment for ZyntroAI
#>
$ErrorActionPreference = "Stop"

Write-Host "🔧 Setting up MCP Environment..." -ForegroundColor Cyan

# 1. Create .env
if (-not (Test-Path .env)) {
    Copy-Item .env.mcp .env
    Write-Host "✅ Created .env from template — please edit with your tokens" -ForegroundColor Green
}

# 2. Create directories
"data", "src", "docs", "config", "scripts" | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -ItemType Directory -Force | Out-Null }
}
Write-Host "✅ Directory structure ready" -ForegroundColor Green

# 3. Check npx
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npx not found — install Node.js 20+: https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js/npx available" -ForegroundColor Green

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "📁 Config: $(Get-Location)\mcp-config.json"
Write-Host "📝 Edit .env → then add config to your MCP client"
```

---

## 🛡️ `.gitignore` — Add These Lines
```gitignore
# ─── MCP / Secrets ─────────────────────────────────
.env
.env.*
!.env.mcp

# ─── Data ──────────────────────────────────────────
data/*.db
data/*.sqlite*

# ─── Node ───────────────────────────────────────────
node_modules/
.npmrc

# ─── Logs ───────────────────────────────────────────
*.log
```

---

## 🖥️ Client-Specific Installation Formats

### Option A — Claude Desktop
**Config location:**
- macOS: `~/Library/Application Support/Claude/mcp_config.json`
- Windows: `%APPDATA%\Claude\mcp_config.json`
- Linux: `~/.config/Claude/mcp_config.json`

Copy the `mcpServers{...}` block from above into the file.

### Option B — VS Code / Cursor
Add to **User Settings → mcp.servers**:
```json
{
  "mcp.servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem@0.6.0", "${workspaceFolder}/src"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github@0.6.0"],
      "env": {
        "GITHUB_TOKEN": "ghp_yourActualTokenHere"
      }
    }
  }
}
```
> Replace placeholders with **actual values** here — VS Code doesn’t expand `${workspace}` the same way.

### Option C — Cursor AI
**Settings → Features → MCP → Add Server**, paste:
```json
{
  "name": "zyntro-filesystem",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem@0.6.0", "/full/path/to/your/src"]
}
```

---

## ✅ Validation & Test
```bash
# Make executable & run setup
chmod +x setup-mcp.sh
./setup-mcp.sh

# Test one server manually
npx @modelcontextprotocol/server-filesystem@0.6.0 ./src

# Verify JSON syntax
node -e "JSON.parse(require('fs').readFileSync('mcp-config.json')); console.log('✅ JSON Valid')"
```

---

## 📌 Version Reference
Current pinned versions (verify latest with `npm view <pkg> version`):
| Server | Version | Purpose |
|---|---|---|
| `server-filesystem` | 0.6.0 | Controlled file access |
| `server-github` | 0.6.0 | Repo/PR management |
| `server-sqlite` | 0.5.0 | Local structured data |
| `server-brave-search` | 0.6.0 | Internet search |
| `server-memory` | 0.6.0 | Persistent memory across sessions |
| `server-postgres` | 0.5.0 | Enterprise DB (disabled by default) |

---

Would you like me to add **a startup health-check script, Cursor/Claude auto-discovery config, or integration hooks linking these MCP servers to your earlier FastAPI/workflow system**?

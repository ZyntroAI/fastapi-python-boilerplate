Perfect! Below is a **complete, ready-to-drop customization bundle** — tailored to your stack (Python/TSX/FastAPI/Obsidian) — with **Skill + Rule + MCP config** all in one place. You can copy these directly into your repo.

---

# 📦 Antigravity Customization Bundle — Python / TSX / FastAPI / Obsidian

## 🧩 1. Code Review & Quality Skill

**File:** `.agents/skills/project-code-review/SKILL.md`

```markdown
---
name: project-code-review
description: Review Python, TSX, FastAPI, and Obsidian plugin code. Checks types, security, error handling, FastAPI best practices, and Obsidian API conventions. Use for PRs, pre-commit, or code quality checks.
---

# Project Code Review Skill

## When to use this skill
- Reviewing pull requests or changed code
- Checking code before commit / pre-commit
- Refactoring or auditing Python, TSX, FastAPI, or Obsidian plugins
- Verifying types, security, and error handling

## Step-by-Step Review Checklist

### 🐍 Python / FastAPI
1. **Types & Signatures**: All public functions have type hints; request/response models use Pydantic; `response_model` is set on routes.
2. **Security**: No hardcoded secrets; inputs validated; auth dependencies applied to protected routes; SQL/NoSQL queries parameterized.
3. **Error Handling**: Proper HTTP status codes; structured exceptions; meaningful messages; no bare `except:`.
4. **FastAPI Conventions**: Dependencies injected; `APIRouter` used; endpoints grouped; docstrings on routes; CORS/config set appropriately.
5. **Structure**: Separated routes/schemas/services; no business logic in `main.py`.

### ⚛️ TSX / TypeScript
1. **Types**: Strict mode enabled; no `any` unless explicitly justified; props/interfaces defined.
2. **React/TSX**: Hooks called correctly; no conditionals inside hooks; cleanup in `useEffect`.
3. **Obsidian Plugins**: Use Obsidian API properly; lifecycle (`onload`/`onunload`) cleaned up; settings defined; no direct DOM access without API; async/await on file I/O.

### 🔒 General Standards
- No credentials, tokens, or secrets committed
- Docstrings / JSDoc on all public APIs
- Line length ≤ 100 chars; consistent naming
- Tests exist for critical paths
- No `console.log` / `print` in production code

## Feedback Format
- **✅ Looks Good**: If all checks pass
- **⚠️ Suggestion**: Improvements, not blocking
- **❌ Issue**: Must fix before merge — explain why + suggest fix
```

---

## 📏 2. Project-Wide Coding Rules

**File:** `.agents/rules/project-standards.md`

```markdown
---
glob: "*.py,*.ts,*.tsx,*.md"
---

# Project Coding Standards — Always Applied

## 🐍 Python / FastAPI
- Use **type hints** for all function signatures
- Use **Pydantic models** for request & response bodies
- Dependencies in FastAPI routes via `Depends()`
- All database access via parameterized queries
- Handle exceptions — **never bare `except:`**
- Use `logging` not `print()`
- Auth required on all non-public routes

## ⚛️ TypeScript / TSX / Obsidian
- Strict TypeScript enabled — no implicit `any`
- Obsidian plugin: clean up events in `onunload()`
- Use `async/await` for file I/O and API calls
- Keep component logic focused — avoid 500-line files
- No inline secrets or API keys — use settings/env vars

## 📝 Documentation
- README.md updated with new features
- API endpoints documented in docstrings
- Plugin settings described in README
- Breaking changes noted

## 🔐 Security — Non-Negotiable
- No hardcoded credentials anywhere
- All user input validated
- CORS origins explicitly configured
- Secrets from env vars or secret manager
```

---

## 🔌 3. MCP Configuration (FastAPI + Dev Tools)

**File:** `.agents/mcp_config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspace}"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "${workspace}/data/app.db"]
    }
  }
}
```

---

## 📁 4. Directory Structure — Where Everything Goes

```
fastapi-python-boilerplate/
├── .agents/
│   ├── skills/
│   │   └── project-code-review/
│   │       └── SKILL.md          ← Code review instructions
│   ├── rules/
│   │   └── project-standards.md  ← Always-on coding rules
│   └── mcp_config.json            ← MCP server connections
├── src/
│   ├── api/      ← FastAPI routes
│   ├── core/     ← Config, auth, dependencies
│   └── obsidian/ ← Plugin code
└── README.md
```

---

## ✅ Quick Setup — Copy & Activate

```bash
# Create directories
mkdir -p .agents/skills/project-code-review .agents/rules

# Paste each file above into its path
# Then verify discovery:
/skills    # → should list "project-code-review"
/mcp       # → should show filesystem, github, sqlite connected
```

---

## 🎯 How to Use

| Task | What to Type |
| --- | --- |
| Review changed code | `/project-code-review review these changes` |
| Auto-review all files | `/goal review every changed file against project standards` |
| Check MCP tools | `/mcp status` |
| See loaded skills | `/skills` |

---

Want me to also create a **PR Workflow** (`/pr-prepare` → runs review + checks + updates docs automatically) so you can invoke one command before opening a PR?

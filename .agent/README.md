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

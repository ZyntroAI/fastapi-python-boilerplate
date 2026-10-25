yaml  
---
title: "AI Agent Skills — Guide & Setup"
type: "guide"
status: "active"
created: "2026-10-25"
updated: "2026-10-25"
tags:
  - ai-agents
  - coding-assistant
  - skills
  - codex
  - claude-code
  - cursor
  - github-copilot
  - typer
related:
  - "[[Typer — Installation & AI Agent Skills Guide]]"
description: "Complete guide to setting up AI Agent Skills for your coding assistant — how they work, supported agents, and best practices"
---
 
 
🤖 AI Agent Skills — Complete Guide
 
Give your AI coding assistant project-specific knowledge instantly ✅
 
 
 
📋 Table of Contents
 
- 🎯 What Are Agent Skills?
- 🧩 Supported AI Agents
- 📦 Quick Setup
- 📁 How It Works — File Structure
- ✍️ Writing Your Own Skills
- 💡 Best Practices
- 🔧 Troubleshooting
 
 
 
🎯 What Are Agent Skills?
 
Agent Skills = Project-specific instructions + reference materials that your AI assistant automatically loads when working in your repository.
 
Instead of explaining your project structure, conventions, and standards every time — your AI already knows them ✅
 
✨ What Skills Can Include:
 
- 📏 Coding conventions & style rules
- 📁 Project structure overview
- 📦 Dependencies and patterns to use/avoid
- 🔑 Common commands and workflows
- 📝 Templates and boilerplate snippets
- ⚠️ Known pitfalls and how to avoid them
 
 
 
🧩 Supported AI Agents
 
Agent Setup Path Status 
🤖 Codex  .codex/skills  ✅ Official 
🎯 Claude Code  .claude/skills  ✅ Official 
🖱️ Cursor  .cursor/rules  ✅ Supported 
🐙 GitHub Copilot  .github/copilot-instructions.md  ✅ Supported 
🔮 Gemini CLI  .gemini/skills  ✅ Supported 
💻 OpenCode  .opencode/skills  ✅ Supported 
📱 Pi  .pi/skills  ✅ Supported 
 
💡 Most agents use a standard Markdown format — write once, works across multiple tools!
 
 
 
📦 Quick Setup
 
Option A — Using  uvx library-skills  (Recommended)
 
bash  
# Run from your project root
uvx library-skills
 
 
- Scans your  pyproject.toml  /  requirements.txt 
- Detects installed libraries
- Automatically generates skills for them
- Lets you choose which AI agents to set up ✅
 
Option B — Manual Setup
 
bash  
# Create skills directory for your agent
mkdir -p .claude/skills
# or
mkdir -p .codex/skills
 
 
 
 
📁 How It Works — File Structure
 
plaintext  
your-project/
├── .claude/
│   └── skills/
│       ├── project-overview.md      # What this project is about
│       ├── coding-standards.md     # How to write code here
│       ├── architecture.md         # How the system is organized
│       └── dependencies.md          # What libraries to use
├── .github/
│   └── copilot-instructions.md     # GitHub Copilot
├── src/
├── tests/
└── pyproject.toml
 
 
🧠 When you open your project: Your AI agent automatically reads all  .md  files in the skills folder — no extra steps needed!
 
 
 
✍️ Writing Your Own Skills
 
📄 Example 1:  .claude/skills/project-overview.md 
 
markdown  
---
name: Project Overview
description: What this project does and its goals
---

# FastAPI Python Boilerplate

## Purpose
A production-ready FastAPI backend template with:
- Clean route-based structure
- Pydantic for data validation
- Health check endpoints
- CI/CD via GitHub Actions

## Tech Stack
- Python 3.11+
- FastAPI 0.115+
- Pydantic Settings
- Uvicorn
- pytest for testing
 
 
📄 Example 2:  .claude/skills/coding-standards.md 
 
markdown  
---
name: Coding Standards
description: Rules for writing code in this project
---

# Coding Standards

## Python Style
- Use **snake_case** for functions and variables
- Use **PascalCase** for classes
- Use type hints everywhere
- Max line length: 100 characters

## Imports Order
1. Standard library
2. Third-party packages
3. Local modules

## FastAPI Patterns
- Define response models in the same route file or separate schemas/ folder
- Use `HTTPException` for error handling
- Add docstrings to all public endpoints
- Pydantic models go in `api/schemas/`
 
 
📄 Example 3:  .claude/skills/testing.md 
 
markdown  
---
name: Testing Guidelines
description: How tests are structured and run
---

# Testing Guide

## Running Tests
```bash
pytest tests/ -v --cov=.
 
 
What to Test
 
- ✅ All API endpoints return expected status codes
- ✅ Input validation works correctly
- ✅ Edge cases and error handling
- ❌ Do NOT test Pydantic library itself — test your logic only
 
Test File Naming
 
- Test files:  test_module_name.py 
- Test functions:  test_function_name() 
 
plaintext  

---

## 💡 Best Practices

### ✅ Do
- ✅ Keep skills files **concise** — under 500 lines each
- ✅ Use clear filenames — `api-structure.md` > `note3.md`
- ✅ Update skills when you change major architecture decisions
- ✅ Include **examples** — "Prefer X over Y because…"
- ✅ Commit skills to Git — everyone on the team gets the same AI context

### ❌ Don't
- ❌ Don't put sensitive data/secrets in skills files
- ❌ Don't write overly long documents — AI may not read everything
- ❌ Don't duplicate information — reference one skill from another

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| AI ignores my skills | Restart your agent/IDE — it may need to reload the files |
| Skills not detected | Check folder name matches your agent exactly (`.claude/skills` not `claude/`) |
| Too much context | Split large files into smaller, focused ones |
| Agent hallucinates anyway | Be explicit: "Do NOT use X library — use Y instead" |

---

## 🗺️ Recommended Skill Set for Your Project

| File | Purpose | Priority |
|---|---|---|
| `project-overview.md` | What & why of the project | 🔴 Must-have |
| `coding-standards.md` | Style, conventions, patterns | 🔴 Must-have |
| `api-structure.md` | Routes, request/response patterns | 🟡 High |
| `testing-guide.md` | How to write & run tests | 🟡 High |
| `dependencies.md` | What's installed, what to use | 🟡 Medium |
| `common-pitfalls.md` | Known issues & how to avoid | 🟢 Nice to have |

---

> 🚀 **Start simple:** Begin with just `project-overview.md` and `coding-standards.md` — add more as your project grows!

Want me to generate a full set of skills files tailored specifically for your **fastapi-python-boilerplate** project? Just say the word! 😊
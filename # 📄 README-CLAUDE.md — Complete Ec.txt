# 📄 README-CLAUDE.md — Complete Ecosystem Guide
> 📍 Path: `README-CLAUDE.md` — For your team & future reference

```markdown
# 🤖 Claude REST API — Full Ecosystem Guide
**Repo:** ZyntroAI/fastapi-python-boilerplate  
**Last Updated:** 2026-09-08 · **API Version:** 2026-01-01

---

## 📋 Overview

This ecosystem integrates **Claude REST API** into your FastAPI boilerplate with full production-grade features: authentication, async client, streaming, function calling, prompt caching, cost tracking, budget controls, auto-knowledge storage, and real-time observability.

---

## 🧱 Architecture — 7 Layers

```
┌─────────────────────────────────────────────────────────────┐
│                  🧠 SKILLS / KNOWLEDGE LAYER                 │
│  Claude Skill Bridge → Auto-Save → Knowledge Artifact Engine │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│               📡 API ROUTES / ENDPOINTS                      │
│  /claude/chat · /stream · /tools · /usage · /budget         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│             🤖 ASYNC API CLIENT — app/claude_client.py       │
│  Chat · Streaming · Tools · Prompt Caching (~90% OFF)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌──────────────┐ ┌────────────┐ ┌──────────────────┐
│ 💰 COST &    │ │ 🛡️ BUDGET  │ │ 📊 OBSERVABILITY │
│ OBSERVABILITY│ │  ALERTS    │ │  GRAFANA + LOKI  │
│ Calculator   │ │ Weekly Limit│ │ Real-Time Logs   │
│ Cache Savings│ │ Auto-Throttle│ │ Dashboards       │
└──────────────┘ └────────────┘ └──────────────────┘
```

---

## 📁 File Reference

| File | Purpose |
|---|---|
| `app/claude_client.py` | Async API Client — Chat · Stream · Tools · Caching |
| `app/claude_observability.py` | Cost Calculator · Cache Savings · Usage Metrics |
| `app/claude_budget_alerts.py` | Weekly Budget · Alerts · Auto-Throttle |
| `skills/claude-integration.py` | Skill Bridge · Auto-Knowledge · Loki Logging |
| `app/api/v1/endpoints/claude.py` | REST API Endpoints |
| `app/grafana_dashboard.json` | Dashboard Spec — Import to Grafana |
| `infrastructure/docker-compose.observability.yml` | Loki + Grafana + Promtail Stack |
| `infrastructure/promtail-config.yml` | Log Shipper Config |
| `infrastructure/grafana-provisioning/` | Auto-Config Datasource & Dashboard |
| `docs/claude-rest-api.md` | Full API Reference Guide |

---

## 🔑 Quick Start

### 1. Set Environment
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start API
```bash
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

### 4. Start Observability Stack (Optional)
```bash
cd infrastructure
docker compose -f docker-compose.observability.yml up -d
# → Grafana: http://localhost:3000  (admin / admin123)
```

---

## 📡 API Endpoints

| Method | Endpoint | Feature |
|---|---|---|
| `POST` | `/claude/chat` | Standard chat — complete response |
| `POST` | `/claude/chat/stream` | SSE streaming — token-by-token |
| `POST` | `/claude/chat/tools` | Function calling — returns tool calls |
| `GET` | `/claude/models` | List supported models |
| `GET` | `/claude/usage/summary` | Cost & cache summary (7-day) |
| `GET` | `/claude/budget/status` | Weekly spending vs limit |
| `POST` | `/claude/budget/config` | Set weekly budget limit |

### Example Request
```bash
curl -X POST http://localhost:8000/claude/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Explain FastAPI briefly"}]
  }'
```

---

## 🧠 Skill Usage (From Any Python Code)

```python
from skills.claude-integration import ClaudeSkill

claude = ClaudeSkill()

# Simple question → auto-saves to knowledge
resp = await claude.ask("Summarize this doc...")
print(resp["text"])
print(resp["cost"])           # $ spent
print(resp["cache_hit_ratio"]) # 0.0–1.0
print(resp["artifact_id"])     # saved knowledge ID

# Multi-turn with tools
resp = await claude.chat(messages, tools=tools_list)

# Auto-summarize
resp = await claude.summarize(long_text, max_words=50)
```

---

## 💡 Key Features Explained

### 1. Prompt Caching (~90% Savings)
- System prompts marked `cache_control: ephemeral`
- Repeated calls → cache hit → **~90% discount** on input tokens
- Auto-enabled — no extra code needed

### 2. Cost Tracking
- Real-time USD calculation per model
- Cache savings reported in every response
- Weekly summary at `/claude/usage/summary`

### 3. Budget Guard (Auto-Throttle)
- Default: **$5/week**
- Alerts at: **50% → 75% → 90%**
- **Auto-blocks** at 95% → prevents bill shock

### 4. Auto-Knowledge Artifacts
- Every response → auto-saved as structured knowledge
- Stored in Asset-Management → searchable & versioned
- Future queries → retrieve from cache → avoid re-asking Claude

### 5. Real-Time Dashboard
- Grafana + Loki stack → one `docker compose` command
- Visualize: Spend · Cache Hit Ratio · Savings · Latency · Calls/hour

---

## 💰 Model Pricing Reference (2026-09)

| Model | Input / 1M | Output / 1M | Cache Read |
|---|---|---|---|
| Opus | $15.00 | $75.00 | ~$1.50 |
| **Sonnet** ⭐ | $3.00 | $15.00 | ~$0.30 |
| Haiku | $0.25 | $1.25 | ~$0.025 |

> ⭐ **Recommended for production:** Best balance of speed, cost, and capability.

---

## 🧪 Tests
```bash
pytest tests/test_claude_client.py -v
```

---

## 📚 Related Skills in Ecosystem

- **url-learning** → Pull latest docs → Claude → Knowledge
- **text-to-skills** → Convert specs → reusable skills
- **debug-error** → Diagnose API failures
- **create-knowledge-artifact** → Auto-store Claude responses
- **asset-management** → Versioned storage for all artifacts

---

## ✅ Best Practices

- ✅ **Use Sonnet** for production — best value
- ✅ **Set system prompts** → auto-cached → big savings
- ✅ **Monitor `/claude/budget/status`** weekly
- ✅ **Check `cache_hit_ratio`** — aim for >80%
- ✅ **Reuse saved knowledge** → avoid redundant API calls
- ✅ **Rotate API keys** regularly via environment variables

---

*Maintained by ZyntroAI · Updated: 2026-09-08*
```

---

## 🚀 Commit & Push
```bash
git add README-CLAUDE.md
git commit -m "docs: add complete Claude ecosystem guide"
git push origin main
```

---

## ✅ 🎉 ALL DONE!

Your repository now has a **complete, production-ready Claude ecosystem** — from API client to cost control, knowledge management, and real-time dashboards — all documented in one guide for your team.

Want me to generate a **CHANGELOG.md** entry or open a **Pull Request** with all these files? 📋✅
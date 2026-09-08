# 📦 Claude REST API — Full Knowledge & Skill Package (Ready-to-Export)

---

## 📁 Structure to Save in Your Project
```
knowledge/
└── documents/
    └── skill/
        └── claude-rest-api.md   ← Main doc below
skills/
└── claude-rest/
    ├── SKILL.md
    ├── client/
    ├── adapters/
    ├── routing/
    ├── middleware/
    └── tests/
```

---

## 📄 `knowledge/documents/skill/claude-rest-api.md`
```markdown
# 🧠 Claude REST API — Official Skill & Knowledge Base
**Updated:** 2026-09-08 | **Base URL:** `https://api.anthropic.com` | **API Version:** `2023-06-01`

---

## 📌 Overview
Anthropic Claude API is a **REST interface** with:
- ✅ **Messages API:** Core chat/completion endpoint
- ✅ **Managed Agents:** Infrastructure for AI agents
- ✅ **SDK Support:** Python / TypeScript / Go / Java / Ruby / PHP / C#
- ✅ **Key Models (2026):** `claude-opus-5`, `claude-sonnet-5`, `claude-fable-5`, `claude-haiku-4-5`
- ❌ **Retired:** `Opus 4.1`, `Sonnet 4` — avoid hardcoding

---

## 📡 Core Endpoints
```http
POST /v1/messages                  # 🎯 Primary: Chat/completion
GET  /v1/models                    # List models (newest first)
POST /v1/messages/count_tokens    # Count tokens
POST /v1/messages/batches         # Batch processing
GET  /v1/messages/batches/{id}    # Get batch status
```

---

## 🧪 Minimal Request
### cURL
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-5",
    "max_tokens": 1024,
    "messages": [{"role":"user","content":"Explain Kubernetes in 3 sentences."}]
  }'
```

### Python (Adapter Pattern)
```python
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system="You are a production coding agent.",
    messages=[{"role":"user","content":"Analyze this repository."}]
)

for block in response.content:
    if block.type == "text":
        print(block.text)
```

---

## 🧭 Model Routing & Lifecycle
### ✅ Active Models
- `claude-opus-5` — Highest intelligence
- `claude-sonnet-5` — Balanced production
- `claude-fable-5` — Creative/verbal
- `claude-haiku-4-5` — Fast/throughput
- Backups: `claude-opus-4-8`, `claude-sonnet-4-6`

### 📋 Recommended Router Config
```yaml
models:
  coding:
    default: claude-sonnet-5
    complex: claude-opus-5
  reasoning:
    default: claude-opus-5
  high_throughput:
    default: claude-haiku-4-5
  fallback: [claude-opus-4-8, claude-sonnet-4-6]
```

---

## 🧱 Architecture: Adapter + Router
**Never call API directly — wrap for production:**
```
Agent Skill
    ↓
AI Provider Router
    ├─ Claude REST Adapter
    ├─ Gemini Adapter
    └─ OpenAI Adapter
    ↓
Model Router → Cost Control → Token Manager → OpenTelemetry
```
**Benefits:**
- ✅ Model fallback/failover
- ✅ Unified rate-limit/retry
- ✅ Tracing + cost tracking
- ✅ Switch providers without rewrite

---

## 📂 Claude REST Skill Folder Structure
```
skills/claude-rest/
├── SKILL.md                 # Overview/usage
├── client/
│   ├── messages.py          # API calls
│   ├── models.py            # Model listing/discovery
│   ├── batches.py           # Batch jobs
│   ├── streaming.py         # SSE stream handler
│   └── errors.py            # Typed exceptions
├── adapters/
│   ├── anthropic.py         # Native adapter
│   ├── bedrock.py           # AWS Bedrock
│   └── vertex.py            # GCP Vertex
├── routing/
│   ├── model-router.py
│   ├── fallback.py
│   └── policy.py
├── middleware/
│   ├── auth.py
│   ├── rate-limit.py
│   ├── retry.py
│   ├── tracing.py
│   └── cost-control.py
└── tests/
```

---

## ⚡ Streaming & Tool Use
### 📺 Real-Time Stream
```http
POST /v1/messages?stream=true → SSE Event Stream
```
**Use cases:** Chat UI, CLI, long reasoning, progress agents

### 🛠️ Built-in Tools
- GitHub, Filesystem, Terminal, Web Search, Database, Kubernetes, Deployment
- Supports **structured output** + **code execution**

---

## 🧠 Prompt Caching & Long Context
### ✅ Best Practice
1. **Order:** System → Skill → Repository → Cached → User
2. **Structure:** Use **XML** for multi-document context
3. **Placement:** Large context **before** query

---

## ❌ Error Format
```json
{
  "type": "error",
  "error": {
    "type": "not_found_error",
    "message": "Resource not found"
  },
  "request_id": "req_..."
}
```
**Use SDK typed exceptions — avoid string parsing**

---

## 🔄 Model Lifecycle Automation
- **Endpoint:** `GET /v1/models` → Auto-discovery
- **Track:** Active / Deprecated / Retired
- **Pipeline:**
  ```
  GET /v1/models → Model Registry → Policy Engine → Select Model → Log → Cost
  ```

---

## ✅ Integration with Your Stack
- ✅ GitHub-Coding Agent
- ✅ Token Management
- ✅ Multi-Agent Orchestration
- ✅ GitHub Actions CI/CD
- ✅ OpenTelemetry / Prometheus / Grafana
```

---

## 📥 Ready to Save
✅ **Complete Markdown doc** — copy into `knowledge/documents/skill/claude-rest-api.md`  
✅ **Folder structure** ready for `skills/claude-rest/`

Would you like me to generate **ZIP archive content** so you can paste directly into repo, or add **`SKILL.md` summary** for the folder? 📦📝

# 🧠 OnSpace.AI × FastAPI — Knowledge Base & Code Examples

คู่มืออ้างอิงสำหรับงาน **FastAPI + OnSpace.AI + CI/CD + Agent Workflow**
ใช้ร่วมกับ [ROADMAP.md](../ROADMAP.md) และ [TASKS.md](../TASKS.md)

---

## 1. หลักการ & เอกสารหลัก

### Core Workflow Principle

```
Merge → Stabilize → Integrate → Build
```

- **Stabilize ก่อน** — แก้ core startup / dependency ให้เสถียรก่อนเพิ่มฟีเจอร์
- **Boundary ชัด** — FastAPI ↔ Service ↔ Provider แยกจากกัน ไม่ข้ามชั้น
- **Safe CI** — SHA-pin ทุก action, ตรวจความปลอดภัยก่อน merge

### สถาปัตยกรรมเป้าหมาย

```
Client → FastAPI → Router → Service Layer → OnSpaceAIService → Provider Factory
```

- **No direct access** — Service ห่อ provider ภายใน Router ไม่แตะ provider ตรง
- **Stateless** — Endpoint ไม่เก็บสถานะเอง (สถานะอยู่ใน pipeline store)
- **Async first** — รองรับ `async`/`await` ตลอด stack

### Best Practices

| หัวข้อ | แนวปฏิบัติ |
| --- | --- |
| FastAPI | Dependency injection, `@lru_cache` สำหรับ singleton, Pydantic v2 |
| Python | Type hints, exception hierarchy, `BackgroundTasks` / worker แยก |
| GitHub | Conventional Commits, PR Template, SHA-pin |
| Agent | ใช้ Service Layer ร่วม — single source of truth |

---

## 2. โค้ด Python (FastAPI + Service Layer)

> ⚠️ **หมายเหตุสำคัญ:** ตัวอย่างในหัวข้อนี้เป็น **แพตเทิร์นเป้าหมาย** สำหรับ Phase 1–2
> โค้ดจริงใน `app/__init__.py` ปัจจุบันเรียก `FastAPIInstrumentor.instrument_app(app)`
> **ก่อน** ที่ `app` จะถูกสร้าง ทำให้ `import app` ล้มด้วย `NameError`
> การย้ายมาใช้ `create_app()` ด้านล่างคือวิธีแก้ที่แนะนำ (ดู Phase 1)

### 📁 `app/__init__.py` — Safe Startup (แยก app factory)

```python
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)


def create_app() -> FastAPI:
    app = FastAPI(
        title="OnSpaceAI FastAPI",
        version="1.0.0",
        description="Stable Core + OnSpace Integration",
    )

    # Security & Rate Limit
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Telemetry — instrument AFTER app exists
    FastAPIInstrumentor.instrument_app(app)

    # Include Routers
    from .api.v1 import router as v1_router
    app.include_router(v1_router, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "version": "1.0.0"}

    @app.get("/metrics", tags=["Observability"])
    async def metrics():
        return {"requests": 0, "latency_ms": 0}

    return app


app = create_app()
```

**จุดที่ต้องระวัง:** ลำดับ import/instrument สำคัญ — instrument ต้องมาหลังสร้าง `app`
และควรย้าย `@app.on_event("startup"/"shutdown")` (deprecated) ไปใช้ `lifespan`

### 📁 `app/service/onspace.py` — Service Layer

```python
from typing import Optional, List
from pydantic import BaseModel
from ..provider.factory import ProviderFactory


class GenerationRequest(BaseModel):
    prompt: str
    model: str = "default"


class GenerationResponse(BaseModel):
    id: str
    status: str
    result: Optional[str] = None


class OnSpaceService:
    def __init__(self):
        self.provider = ProviderFactory.get()

    async def generate(self, req: GenerationRequest) -> GenerationResponse:
        return await self.provider.generate(req)

    async def get_status(self, gen_id: str) -> GenerationResponse:
        return await self.provider.status(gen_id)

    async def list_providers(self) -> List[str]:
        return await self.provider.available()
```

### 📁 `app/api/v1/endpoints.py` — Router

```python
from fastapi import APIRouter, Depends, HTTPException
from ...service.onspace import OnSpaceService, GenerationRequest, GenerationResponse

router = APIRouter()


def get_service():
    return OnSpaceService()


@router.post("/ai/generations", response_model=GenerationResponse)
async def create_generation(
    req: GenerationRequest,
    service: OnSpaceService = Depends(get_service),
):
    try:
        return await service.generate(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/generations/{gen_id}")
async def get_status(gen_id: str, service: OnSpaceService = Depends(get_service)):
    return await service.get_status(gen_id)


@router.get("/ai/providers")
async def list_providers(service: OnSpaceService = Depends(get_service)):
    return await service.list_providers()
```

---

## 3. โค้ด JSX/TSX (Frontend + Agent UI)

### 📁 `components/GenerationCard.tsx`

```tsx
import React from 'react';

type Status = 'pending' | 'running' | 'done' | 'failed';

interface Gen {
  id: string;
  prompt: string;
  status: Status;
  result?: string;
}

interface Props {
  item: Gen;
}

const statusMap: Record<Status, string> = {
  pending: '🕓 รอ',
  running: '🔄 กำลังทำ',
  done: '✅ เสร็จ',
  failed: '❌ ล้มเหลว',
};

export const GenerationCard: React.FC<Props> = ({ item }) => {
  return (
    <div className="border rounded p-4 my-2 bg-white shadow-sm">
      <div className="flex justify-between mb-2">
        <span className="font-mono text-sm text-gray-600">{item.id}</span>
        <span>{statusMap[item.status]}</span>
      </div>
      <p className="mb-2">{item.prompt}</p>
      {item.result && (
        <pre className="text-xs bg-gray-50 p-2 rounded mt-2">{item.result}</pre>
      )}
    </div>
  );
};
```

### 📁 `hooks/useGenerations.ts` — React Query

```tsx
import { useQuery, useMutation } from '@tanstack/react-query';

const API = '/api/v1';

export const useGenerations = () => {
  return useQuery({
    queryKey: ['generations'],
    queryFn: async () => {
      const res = await fetch(`${API}/ai/generations`);
      if (!res.ok) throw new Error('Failed');
      return res.json();
    },
  });
};

export const useCreateGeneration = () => {
  return useMutation({
    mutationFn: async (prompt: string) => {
      const res = await fetch(`${API}/ai/generations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      return res.json();
    },
  });
};
```

---

## 4. CI/CD — SHA-Pinned Workflow

> 🔴 **สถานะปัจจุบัน (2026-09-11):** CI ล้มทุก job ที่ขั้น *Set up job* เพราะ repo บังคับ
> ให้ทุก action pin เป็น commit SHA เต็ม แต่ workflow ยังใช้ `@v4` / `@v5` อยู่
> และ `scan` job pin ไปยัง SHA ที่ **resolve ไม่ได้**
> ต้องแก้ที่ **Phase 7** — ดูรายการ action ที่ต้อง pin ใน [ROADMAP.md](../ROADMAP.md)

```yaml
name: FastAPI CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.12"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      # ⚠️ ต้องแทน @v4 ด้วย commit SHA เต็ม (40 ตัวอักษร)
      - uses: actions/checkout@<SHA>
      - uses: actions/setup-python@<SHA>
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - run: pip install ruff
      - run: ruff check .

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<SHA>
      - uses: actions/setup-python@<SHA>
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

---

## 5. เอกสารอ้างอิงเพิ่มเติม

### Service Contract — ขอบเขตแต่ละชั้น

| ชั้น | รับผิดชอบ |
| --- | --- |
| **FastAPI** | Request/Response, Auth, Rate Limit |
| **Service** | Logic, State, Error Mapping |
| **Provider** | External/Internal API, Retry, Timeout |

### Security Rules

- ✅ SHA-pin ทุก action
- ✅ No secrets in logs
- ✅ Pydantic validation ทุก input
- ✅ CORS, OAuth2, JWT

# pure-agent-dev

> Reference implementation for **Issue #63** — *"Code Guide: pure-agent-dev"*.
> Provider-agnostic agent skeleton on FastAPI, with BytePlus ECS as the first
> adapter. Lives in `deliverables/` per repo convention and does not touch the
> main application tree.

## The one rule

> **The Agent must never depend on the BytePlus SDK.**

Dependency direction, enforced by `tests/test_architecture.py`:

```
API -> Services -> Agents -> Provider Interface -> Adapter -> Cloud SDK
```

Never:

```
Agent -> Cloud SDK
```

That direction is what lets you change cloud provider, add agents, or add tasks
without re-architecting. Swap an adapter and nothing above it moves.

## Layout

```
pure-agent-dev/
├── pure_agent/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # provider selection (not hard-coded in agents)
│   ├── api/
│   │   ├── deps.py             # DI: provider chosen here, injected downward
│   │   └── routes/             # health.py, tasks.py, compute.py
│   ├── agents/
│   │   ├── planner.py          # intent -> AgentTask
│   │   └── executor.py         # AgentTask -> provider (via the interface)
│   ├── providers/
│   │   ├── base.py             # ComputeProvider (ABC)  <- the key abstraction
│   │   ├── mock.py             # in-memory provider, CI needs no credentials
│   │   └── byteplus/
│   │       ├── client.py       # credentials/region/SDK init only
│   │       └── ecs.py          # implements ComputeProvider
│   ├── schemas/                # Pydantic runtime models
│   └── services/               # business orchestration
├── schemas/agent-task.schema.json   # external contract (JSON Schema)
├── tests/                      # unit + contract + architecture + API
├── agent.yaml                  # declarative configuration
├── Dockerfile / docker-compose.yml
└── .github/workflows/ci.yml
```

## Run

```bash
pip install -r requirements-dev.txt

uvicorn pure_agent.main:app --reload     # http://localhost:8000/docs
pytest -q                                # no cloud credentials needed
ruff check .
```

Docker:

```bash
cp .env.example .env
docker compose up --build
```

## Provider selection

Set `COMPUTE_PROVIDER` (`mock` default, or `byteplus`). The value is read once in
`config.py` and wired in through FastAPI's dependency injection — routes and
agents never import an adapter directly, so this is a config change, not a code
change:

```bash
COMPUTE_PROVIDER=byteplus \
BYTEPLUS_ACCESS_KEY=... BYTEPLUS_SECRET_KEY=... \
uvicorn pure_agent.main:app
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Liveness. Dependency-free by design. |
| `POST` | `/v1/tasks` | Run a structured `AgentTask`. |
| `GET` | `/v1/compute/instances` | List instances. |
| `POST` | `/v1/compute/instances/{id}/start` | Start. |
| `POST` | `/v1/compute/instances/{id}/stop` | Stop. |
| `POST` | `/v1/compute/instances/{id}/reboot` | Reboot. |

```bash
curl -X POST localhost:8000/v1/tasks -H 'content-type: application/json' \
  -d '{"task_id":"t-1","action":"start_instance","instance_id":"i-mock-001"}'
```

## Two contracts, on purpose

`AgentTask` is defined twice, and both are checked against each other in
`tests/test_schema_contract.py`:

- `schemas/agent-task.schema.json` — the **external** contract other services and
  agents rely on.
- `pure_agent/schemas/task.py` — the **runtime** model that validates in-process.

## Adding a provider (AWS example)

Write one adapter and register it — nothing above `providers/` changes:

```python
# pure_agent/providers/aws/ecs.py
from pure_agent.providers.base import ComputeProvider
from pure_agent.schemas.compute import InstanceResponse

class AWSEcsProvider(ComputeProvider):
    async def list_instances(self) -> list[InstanceResponse]:
        return []
    async def start_instance(self, instance_id: str) -> InstanceResponse:
        return InstanceResponse(instance_id=instance_id, status="starting")
    async def stop_instance(self, instance_id: str) -> InstanceResponse:
        return InstanceResponse(instance_id=instance_id, status="stopping")
    async def reboot_instance(self, instance_id: str) -> InstanceResponse:
        return InstanceResponse(instance_id=instance_id, status="rebooting")
```

Then extend `ProviderName` in `config.py` and the branch in `api/deps.py`.

## Status

`providers/byteplus/ecs.py` and `client.py` are **complete in shape, stubbed in
body** — the SDK calls are marked `TODO(byteplus)`. Signatures, return types and
the interface are final; filling in the SDK calls does not touch anything else.
Every test runs on `MockComputeProvider`, so CI needs no cloud credentials.

Verified: `pytest` green, `ruff` clean, provider swap exercised both ways.

---

## สรุปภาษาไทย (สำหรับทีม)

**นี่คืออะไร** — reference implementation ตาม Code Guide ใน Issue #63: โครง Agent บน FastAPI ที่**ไม่ผูกกับผู้ให้บริการคลาวด์รายใดรายหนึ่ง** โดย BytePlus ECS เป็น adapter ตัวแรกที่ต่อไว้

**กฎข้อเดียวที่ทั้งสถาปัตยกรรมนี้ปกป้อง**

> Agent ต้องไม่ depend กับ SDK ของ BytePlus

ทิศทาง dependency ที่บังคับใช้จริง (ไม่ใช่แค่ comment):

```
API -> Services -> Agents -> Provider Interface -> Adapter -> Cloud SDK
```

ห้ามเด็ดขาด: `Agent -> Cloud SDK`

`tests/test_architecture.py` เป็นคนบังคับกฎนี้ — เดินดู import graph จริงและ fail ถ้ามีชั้นไหนทะลุข้าม interface ไปหยิบ adapter ตรง ๆ ดังนั้นกฎจะไม่ถูกละเมิดโดยไม่มีใครรู้

**ทำไมเรื่องนี้สำคัญ** — เพราะวันที่จะเปลี่ยนคลาวด์ (BytePlus → AWS/Azure/GCP) จะไม่ต้องรื้อ Agent, Service หรือ API เลย แก้แค่ adapter ไฟล์เดียว

**โครงสร้างสำคัญ**

| ชั้น | หน้าที่ |
| --- | --- |
| `providers/base.py` | `ComputeProvider` (ABC) — สัญญาที่ทุกคลาวด์ต้อง implement |
| `providers/mock.py` | provider ในหน่วยความจำ — ทำให้ CI ไม่ต้องใช้ credential จริง |
| `providers/byteplus/` | adapter จริง (โครงครบ, ตัวเรียก SDK ยังเป็น TODO) |
| `agents/planner.py` | แปลงคำสั่ง → `AgentTask` (ไม่แตะ provider) |
| `agents/executor.py` | รับ `AgentTask` → เรียก provider ผ่าน interface เท่านั้น |
| `api/deps.py` | จุดเดียวที่เลือก provider แล้ว inject ลงไป |

**วิธีสลับ provider** — เปลี่ยน env var ไม่ใช่แก้โค้ด:

```bash
COMPUTE_PROVIDER=mock       # ค่าเริ่มต้น — รันได้ทันที ไม่ต้องมี credential
COMPUTE_PROVIDER=byteplus   # ต้องมี BYTEPLUS_ACCESS_KEY / SECRET_KEY
```

**สถานะที่ตรวจแล้ว**

- `pytest` ผ่าน **47/47** — รวมโหมด `python -O` (พิสูจน์ว่าไม่มี `assert` ที่ทำหน้าที่เป็น control flow)
- `ruff check .` ผ่านสะอาด
- JSON Schema ภายนอก (`schemas/agent-task.schema.json`) ตรงกับ Pydantic model — มี test เทียบให้ทั้งคู่

**สิ่งที่ยังไม่ได้ทำ** — ตัวเรียก SDK ใน `providers/byteplus/ecs.py` ยังเป็น `TODO(byteplus)` signature และ return type ถูกกำหนดครบแล้ว เหลือแค่เติมการเรียก ECS จริง ซึ่งไม่ต้องแก้ไฟล์อื่นเลย

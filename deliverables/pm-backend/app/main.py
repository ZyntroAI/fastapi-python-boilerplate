"""FastAPI application entrypoint.

Bundles all four equal modules behind one ASGI app:
    /api/csv        - Program Management CSV template generation
    /api/billing    - provider-neutral billing interoperability
    /api/tool       - runtime tool switcher
    /api/programs   - program registry (exercises opt-in encryption at rest)
"""
from __future__ import annotations

import io

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import billing, pm_csv, tool_switcher
from .billing import (
    ProviderAuthError,
    ProviderError,
    ProviderNotFoundError,
)
from .config import Settings, get_settings
from .db import get_db, init_db
from .repository import create_program, get_program, list_programs

app = FastAPI(
    title="Program Management Backend",
    version=get_settings().version,
    description=(
        "Integrated backend with Program Management CSV generation, "
        "billing interoperability, a tool switcher, and opt-in "
        "database encryption at rest (ENCRYPT_AT_REST)."
    ),
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health", tags=["system"])
def health(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "encrypt_at_rest": settings.encrypt_at_rest,
        "billing_provider": settings.billing_provider,
        "active_tool": tool_switcher.current_tool(),
    }


# --------------------------------------------------------------------------
# Tool switcher
# --------------------------------------------------------------------------

class ToolSwitchIn(BaseModel):
    tool: str = Field(..., description="One of pm_csv, billing, settings")


@app.get("/api/tool", tags=["tool-switcher"])
def get_active_tool() -> dict:
    return {"active_tool": tool_switcher.current_tool(), "tools": tool_switcher.list_tools()}


@app.post("/api/tool", tags=["tool-switcher"])
def switch_tool(body: ToolSwitchIn) -> dict:
    try:
        active = tool_switcher.set_tool(body.tool)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"active_tool": active, "tools": tool_switcher.list_tools()}


# --------------------------------------------------------------------------
# Program Management CSV
# --------------------------------------------------------------------------

class ProgramRowsIn(BaseModel):
    rows: list[dict] = Field(default_factory=list)


@app.get("/api/csv/template", tags=["pm-csv"])
def csv_template() -> StreamingResponse:
    content = pm_csv.template_csv()
    return StreamingResponse(
        io.StringIO(content),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="program_template.csv"'
        },
    )


@app.post("/api/csv/generate", tags=["pm-csv"])
def csv_generate(body: ProgramRowsIn) -> dict:
    try:
        rows = pm_csv.rows_to_csv(body.rows)
    except Exception as exc:  # pydantic validation
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"csv": rows, "count": len(body.rows)}


@app.post("/api/csv/validate", tags=["pm-csv"])
def csv_validate(body: ProgramRowsIn) -> dict:
    """Validate rows against the PM CSV schema and return errors per row."""
    errors: list[dict] = []
    for idx, raw in enumerate(body.rows):
        try:
            pm_csv.ProgramRow(**raw)
        except Exception as exc:
            errors.append({"row": idx, "error": str(exc)})
    return {"valid": not errors, "errors": errors, "count": len(body.rows)}


# --------------------------------------------------------------------------
# Billing interoperability
# --------------------------------------------------------------------------

_provider_cache: dict[tuple, billing.BillingProvider] = {}


def _provider(settings: Settings = Depends(get_settings)) -> billing.BillingProvider:
    """Return a cached billing provider so stub state persists between calls."""
    key = (settings.billing_provider, settings.billing_api_key, settings.billing_base_url)
    if key not in _provider_cache:
        try:
            _provider_cache[key] = billing.build_provider(
                provider=settings.billing_provider,
                api_key=settings.billing_api_key,
                base_url=settings.billing_base_url,
            )
        except ProviderAuthError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _provider_cache[key]


class CustomerCreateIn(BaseModel):
    email: str = Field(..., min_length=3)
    name: str = ""


class InvoiceCreateIn(BaseModel):
    customer_id: str = Field(...)
    amount: int = Field(..., gt=0, description="Amount in minor units (cents)")
    currency: str = "usd"
    description: str = ""


class ChargeIn(BaseModel):
    customer_id: str = Field(...)
    amount: int = Field(..., gt=0)
    currency: str = "usd"


@app.get("/api/billing/provider", tags=["billing"])
def billing_provider_info(
    provider: billing.BillingProvider = Depends(_provider),
) -> dict:
    return provider.health()


@app.post("/api/billing/customers", tags=["billing"])
def billing_create_customer(
    body: CustomerCreateIn,
    provider: billing.BillingProvider = Depends(_provider),
) -> dict:
    try:
        c = provider.create_customer(body.email, body.name)
    except ProviderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return c.model_dump()


@app.post("/api/billing/invoices", tags=["billing"])
def billing_create_invoice(
    body: InvoiceCreateIn,
    provider: billing.BillingProvider = Depends(_provider),
) -> dict:
    try:
        inv = provider.create_invoice(
            body.customer_id, body.amount, body.currency, body.description
        )
    except ProviderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return inv.model_dump()


@app.post("/api/billing/charges", tags=["billing"])
def billing_charge(
    body: ChargeIn,
    provider: billing.BillingProvider = Depends(_provider),
) -> dict:
    try:
        pi = provider.charge(body.customer_id, body.amount, body.currency)
    except ProviderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return pi.model_dump()


# --------------------------------------------------------------------------
# Program registry (encryption at rest on the note column)
# --------------------------------------------------------------------------

class ProgramCreateIn(BaseModel):
    name: str = Field(..., min_length=1)
    owner: str = ""
    status: str = "planned"
    note: str = ""


class ProgramOut(BaseModel):
    id: str
    name: str
    owner: str = ""
    status: str = ""
    note: str = ""


@app.post("/api/programs", tags=["programs"])
def api_create_program(
    body: ProgramCreateIn, db: Session = Depends(get_db)
) -> ProgramOut:
    rec = create_program(
        db, name=body.name, owner=body.owner, status=body.status, note=body.note
    )
    return ProgramOut(id=rec.id, name=rec.name, owner=rec.owner, status=rec.status, note=rec.note)


@app.get("/api/programs", tags=["programs"])
def api_list_programs(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
) -> list[ProgramOut]:
    return [
        ProgramOut(id=r.id, name=r.name, owner=r.owner, status=r.status, note=r.note)
        for r in list_programs(db)[:limit]
    ]


@app.get("/api/programs/{program_id}", tags=["programs"])
def api_get_program(program_id: str, db: Session = Depends(get_db)) -> ProgramOut:
    rec = get_program(db, program_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="program not found")
    return ProgramOut(id=rec.id, name=rec.name, owner=rec.owner, status=rec.status, note=rec.note)

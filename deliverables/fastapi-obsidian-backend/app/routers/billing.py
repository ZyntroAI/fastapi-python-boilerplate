"""Billing interoperability - records + CSV export."""
import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..db import db

router = APIRouter(prefix="/billing", tags=["billing"])


class Charge(BaseModel):
    id: str
    amount: float
    currency: str = "USD"
    description: str = ""
    status: str = "pending"


@router.get("/charges")
def list_charges():
    return db.get("charges", [])


@router.post("/charges")
def add_charge(charge: Charge):
    charges = db.get("charges", [])
    charges.append(charge.dict())
    db.set("charges", charges)
    return charge


@router.get("/charges/export")
def export_charges():
    charges = db.get("charges", [])
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "amount", "currency", "description", "status"])
    for c in charges:
        writer.writerow([c["id"], c["amount"], c["currency"], c["description"], c["status"]])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=charges.csv"})

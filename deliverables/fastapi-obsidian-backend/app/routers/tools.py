"""Tool switcher - which modules are active."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import db

router = APIRouter(prefix="/tools", tags=["tools"])

MODULES = ["skills", "programs", "billing"]


class ToolState(BaseModel):
    name: str
    enabled: bool


@router.get("")
def list_tools():
    states = db.get("tool_states", {})
    return [ToolState(name=m, enabled=states.get(m, True)) for m in MODULES]


@router.post("/{name}")
def set_tool(name: str, enabled: bool = True):
    if name not in MODULES:
        raise HTTPException(status_code=404, detail=f"unknown tool '{name}'")
    states = db.get("tool_states", {})
    states[name] = enabled
    db.set("tool_states", states)
    return ToolState(name=name, enabled=enabled)

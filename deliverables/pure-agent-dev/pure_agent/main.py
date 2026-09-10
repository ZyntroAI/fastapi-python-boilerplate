"""FastAPI entry point.

    uvicorn pure_agent.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI

from pure_agent import __version__
from pure_agent.api.routes import compute, health, tasks

app = FastAPI(title="Pure Agent API", version=__version__)

app.include_router(health.router)
app.include_router(tasks.router, prefix="/v1")
app.include_router(compute.router, prefix="/v1")

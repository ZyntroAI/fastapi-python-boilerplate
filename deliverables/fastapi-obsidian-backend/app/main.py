"""Integrated FastAPI backend serving an Obsidian skill library.

Modules: skills (per-user), programs (CSV), billing, tools, security (encryption at rest), auth (JWT).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import db
from .routers import billing, programs, security, skills, tools, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init(encrypt=settings.encrypt_at_rest)
    yield
    db.close()


app = FastAPI(
    title="Integrated Backend (FastAPI + Obsidian)",
    version="1.0.0",
    description="Skills API, programs CSV, billing, tool switcher, JWT auth, encryption at rest",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(skills.router)
app.include_router(programs.router)
app.include_router(billing.router)
app.include_router(tools.router)
app.include_router(security.router)
app.include_router(users.router)


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "integrated-backend",
        "version": "1.0.0",
        "encrypt_at_rest": settings.encrypt_at_rest,
        "docs": "/docs",
        "modules": ["skills", "programs", "billing", "tools", "auth", "security"],
    }

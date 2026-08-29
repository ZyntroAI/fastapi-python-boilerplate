"""
Example endpoint following the fastapi-research skill conventions.
Use case: submit a research document, kick off background embedding,
and expose paginated results — matches the doc_embeddings / pgvector
pipeline noted for CrystalCastle.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/research-docs", tags=["research-docs"])


# --- 1. Separate Create / Response schemas (never reuse one model) -------

class ResearchDocCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, description="Raw markdown/text to embed")
    source_url: str | None = Field(default=None, description="Origin of the document, if any")


class ResearchDocResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    status: str  # "queued" | "embedded" | "failed"
    created_at: datetime


# --- 2. Dependency injection for shared resources ------------------------

async def get_db_session():
    # Replace with your actual Supabase/asyncpg session factory.
    session = await create_session()
    try:
        yield session
    finally:
        await session.close()


DbSession = Annotated[object, Depends(get_db_session)]


# --- 3. Background task for the actual embedding work --------------------

async def embed_document(doc_id: UUID, content: str) -> None:
    """
    Runs after the response is sent. Generates the embedding
    (e.g. sentence-transformers all-MiniLM-L6-v2) and upserts it
    into the pgvector `doc_embeddings` table. Anything over a couple
    seconds belongs here, not in the request/response cycle.
    """
    try:
        vector = await generate_embedding(content)
        await upsert_embedding(doc_id=doc_id, vector=vector)
    except Exception as exc:
        await mark_doc_failed(doc_id, reason=str(exc))


# --- 4. Route handlers ----------------------------------------------------

@router.post("", response_model=ResearchDocResponse, status_code=202)
async def create_research_doc(
    payload: ResearchDocCreate,
    background_tasks: BackgroundTasks,
    db: DbSession,
) -> ResearchDocResponse:
    doc_id = uuid4()
    now = datetime.utcnow()

    await db.execute(
        "insert into research_docs (id, title, content, source_url, status, created_at) "
        "values ($1, $2, $3, $4, 'queued', $5)",
        doc_id, payload.title, payload.content, payload.source_url, now,
    )

    background_tasks.add_task(embed_document, doc_id, payload.content)

    return ResearchDocResponse(id=doc_id, title=payload.title, status="queued", created_at=now)


@router.get("", response_model=list[ResearchDocResponse])
async def list_research_docs(
    db: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ResearchDocResponse]:
    rows = await db.fetch(
        "select id, title, status, created_at from research_docs "
        "order by created_at desc limit $1 offset $2",
        limit, offset,
    )
    return [ResearchDocResponse.model_validate(dict(r)) for r in rows]


@router.get("/{doc_id}", response_model=ResearchDocResponse)
async def get_research_doc(doc_id: UUID, db: DbSession) -> ResearchDocResponse:
    row = await db.fetchrow(
        "select id, title, status, created_at from research_docs where id = $1",
        doc_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="research document not found")
    return ResearchDocResponse.model_validate(dict(row))


# --- Placeholders for the imports referenced above (wire up for real) ----
async def create_session(): ...
async def generate_embedding(text: str) -> list[float]: ...
async def upsert_embedding(doc_id: UUID, vector: list[float]) -> None: ...
async def mark_doc_failed(doc_id: UUID, reason: str) -> None: ...

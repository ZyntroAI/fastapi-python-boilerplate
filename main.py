import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi_mcp import AuthConfig, FastApiMCP

from auth import create_access_token, verify_access_token
from schemas import (
    FeedbackRequest,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    ReindexResponse,
    TokenResponse,
    ValidationResponse,
)
from services.knowledge import (
    build_semantic_index,
    search_semantic_index,
    validate_semantic_cache,
)

load_dotenv()

VAULT_PATH = Path(
    os.getenv("OBSIDIAN_VAULT_PATH", "")
).resolve()

if not VAULT_PATH.exists():
    raise RuntimeError(
        f"Obsidian vault path does not exist: {VAULT_PATH}"
    )

app = FastAPI(
    title="Obsidian Agent OS API",
    version="0.1.0",
    description="FastAPI backend for the Obsidian Agent OS platform.",
)


@app.post(
    "/auth/token",
    response_model=TokenResponse,
    tags=["auth"],
)
async def issue_token() -> TokenResponse:
    """
    Issue a local development token.

    Replace this with a real login flow before exposing
    the service beyond localhost.
    """
    return TokenResponse(
        access_token=create_access_token(
            subject="obsidian-agent-os-bridge"
        )
    )


@app.post(
    "/api/v1/knowledge/search",
    response_model=KnowledgeSearchResponse,
    tags=["knowledge"],
)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    subject: str = Depends(verify_access_token),
) -> KnowledgeSearchResponse:
    results = search_semantic_index(
        query=request.query,
        folder=request.folder,
        limit=request.limit,
        minimum_score=request.minimum_score,
    )

    return KnowledgeSearchResponse(results=results)


@app.post(
    "/api/v1/knowledge/validate",
    response_model=ValidationResponse,
    tags=["knowledge"],
)
async def validate_knowledge(
    subject: str = Depends(verify_access_token),
) -> ValidationResponse:
    return validate_semantic_cache()


@app.post(
    "/api/v1/knowledge/reindex",
    response_model=ReindexResponse,
    tags=["knowledge"],
)
async def reindex_knowledge(
    subject: str = Depends(verify_access_token),
) -> ReindexResponse:
    return build_semantic_index(force_rebuild=True)


@app.post(
    "/api/v1/feedback",
    tags=["feedback"],
)
async def create_feedback(
    request: FeedbackRequest,
    subject: str = Depends(verify_access_token),
) -> dict:
    feedback_id = f"feedback-{int(datetime.now().timestamp() * 1000)}"

    return {
        "id": feedback_id,
        "status": "accepted",
        "type": request.type,
        "severity": request.severity,
        "message": request.message,
        "subject": subject,
    }


token_auth_scheme = HTTPBearer()


async def verify_mcp_token(
    token=Depends(token_auth_scheme),
) -> str:
    if not token.credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing Agent OS token",
        )

    return verify_access_token(token)


mcp = FastApiMCP(
    app,
    name="Obsidian Agent OS MCP",
    description="MCP server for Obsidian knowledge search and validation.",
    auth_config=AuthConfig(
        dependencies=[Depends(verify_mcp_token)]
    ),
)

mcp.mount_http()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
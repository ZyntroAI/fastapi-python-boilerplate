"""Obsidian router - exposes the Local REST API through the app.

Read endpoints are open (they are proxied to the local vault only); write
endpoints require JWT auth and an explicit ``OBSIDIAN_ALLOW_WRITE=1`` opt-in.
When ``OBSIDIAN_API_URL`` is unset the whole module degrades to a clear 503
instead of silently failing requests.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..config import settings
from ..cwe1321_bridge import sanitize_prototype_keys
from ..obsidian import ObsidianClient, ObsidianError, build_patch_instruction
from ..security import get_current_user

router = APIRouter(prefix="/obsidian", tags=["obsidian"])


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #

class NotePayload(BaseModel):
    """Untrusted inbound note body — sanitized before it reaches the vault."""

    content: str = ""
    frontmatter: Dict[str, Any] = Field(default_factory=dict)


class PatchRequest(BaseModel):
    target_type: str = "heading"
    target: Any = None
    operation: str = "append"
    scope: str = "content"
    content: Optional[str] = None
    value: Any = None
    destination: Optional[Dict[str, Any]] = None
    within: Optional[int] = None
    if_match: Optional[str] = None
    create_target_if_missing: bool = False
    reject_if_content_preexists: bool = False


class SearchRequest(BaseModel):
    """JsonLogic query body."""

    query: Dict[str, Any] = Field(default_factory=dict)


def _client() -> ObsidianClient:
    if not settings.obsidian_api_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Obsidian API not connected (set OBSIDIAN_API_URL)",
        )
    return ObsidianClient(
        settings.obsidian_api_url,
        os.environ.get(settings.obsidian_api_key_env, ""),
        allow_write=settings.obsidian_allow_write,
    )


def _handle(exc: ObsidianError) -> HTTPException:
    """Translate client errors into HTTP, never leaking the API key."""
    code = exc.status if 400 <= exc.status < 600 else status.HTTP_502_BAD_GATEWAY
    return HTTPException(status_code=code, detail=exc.message)


# --------------------------------------------------------------------------- #
# Status & reads
# --------------------------------------------------------------------------- #

@router.get("/status")
def obsidian_status() -> Dict[str, Any]:
    """Whether the local vault bridge is configured, and whether writes are on."""
    return {
        "connected": bool(settings.obsidian_api_url),
        "allow_write": settings.obsidian_allow_write,
    }


@router.get("/version")
def api_version() -> Dict[str, Any]:
    """Authenticated call to GET / of the Obsidian API."""
    try:
        return _client().api_version()
    except ObsidianError as exc:
        raise _handle(exc)


@router.get("/vault")
def list_vault(path: str = Query("", description="Optional vault-relative directory")) -> List[str]:
    try:
        client = _client()
        return client.list_dir(path) if path else client.list_vault()
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/note")
def read_note(
    filename: str = Query(..., description="Vault-relative note path") ,
    meta: bool = Query(False, description="Return parsed frontmatter/tags instead of markdown"),
) -> Dict[str, Any]:
    try:
        client = _client()
        if meta:
            note = client.read_note_json(filename)
            return {
                "path": note.path,
                "content": note.content,
                "frontmatter": note.frontmatter,
                "tags": note.tags,
                "stat": note.stat,
            }
        return {"path": filename, "content": client.read_note(filename)}
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/note/map")
def document_map(filename: str = Query(...)) -> Dict[str, Any]:
    """Heading tree + concurrency token for a note."""
    try:
        return _client().document_map(filename)
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/active")
def read_active() -> Dict[str, str]:
    try:
        return {"content": _client().read_active()}
    except ObsidianError as exc:
        raise _handle(exc)


@router.get("/tags")
def list_tags() -> Dict[str, int]:
    try:
        return _client().tags()
    except ObsidianError as exc:
        raise _handle(exc)


@router.get("/commands")
def list_commands() -> List[Dict[str, Any]]:
    try:
        return _client().commands()
    except ObsidianError as exc:
        raise _handle(exc)


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #

@router.post("/search")
def search(body: SearchRequest) -> List[Dict[str, Any]]:
    """JsonLogic search over the vault. The query is sanitized first."""
    try:
        return _client().search(sanitize_prototype_keys(body.query))
    except ObsidianError as exc:
        raise _handle(exc)


@router.post("/search/simple")
def simple_search(
    query: str = Query(..., min_length=1),
    context_length: int = Query(100, ge=1, le=1000),
) -> List[Dict[str, Any]]:
    try:
        return _client().simple_search(query, context_length=context_length)
    except ObsidianError as exc:
        raise _handle(exc)


# --------------------------------------------------------------------------- #
# Writes (JWT + explicit opt-in)
# --------------------------------------------------------------------------- #

@router.put("/note")
def write_note(body: NotePayload, filename: str = Query(...), _user: str = Depends(get_current_user)) -> Dict[str, Any]:
    try:
        _client().write_note(filename, sanitize_prototype_keys(body.content))
        return {"status": "ok", "path": filename, "operation": "put"}
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/note/append")
def append_note(
    body: NotePayload,
    filename: str = Query(...),
    target: Optional[str] = Query(None),
    target_type: str = Query("heading"),
    _user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        client = _client()
        client.append_note(
            filename,
            sanitize_prototype_keys(body.content),
            target_type=target_type if target else None,
            target=target,
        )
        return {"status": "ok", "path": filename, "operation": "append", "target": target}
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.patch("/note")
def patch_note(body: PatchRequest, filename: str = Query(...), _user: str = Depends(get_current_user)) -> Dict[str, Any]:
    """Apply one structured markdown-patch instruction."""
    try:
        instruction = build_patch_instruction(
            body.target_type,
            sanitize_prototype_keys(body.target),
            body.operation,
            scope=body.scope,
            content=body.content,
            value=None if body.value is None else sanitize_prototype_keys(body.value),
            destination=body.destination,
            within=body.within,
            if_match=body.if_match,
            create_target_if_missing=body.create_target_if_missing,
            reject_if_content_preexists=body.reject_if_content_preexists,
        )
        resp = _client().patch_note(filename, instruction)
        return {
            "status": "ok",
            "path": filename,
            "operation": body.operation,
            "document": resp.text,
        }
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/note")
def delete_note(
    filename: str = Query(...),
    permanent: bool = Query(False),
    _user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        _client().delete_note(filename, permanent=permanent)
        return {"status": "ok", "path": filename, "operation": "delete", "permanent": permanent}
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/commands/{command_id}/execute")
def execute_command(command_id: str, _user: str = Depends(get_current_user)) -> Dict[str, Any]:
    try:
        _client().execute_command(command_id)
        return {"status": "ok", "command": command_id}
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/open")
def open_file(
    filename: str = Query(...),
    new_leaf: bool = Query(False),
    _user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        _client().open_file(filename, new_leaf=new_leaf)
        return {"status": "ok", "path": filename, "new_leaf": new_leaf}
    except ObsidianError as exc:
        raise _handle(exc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

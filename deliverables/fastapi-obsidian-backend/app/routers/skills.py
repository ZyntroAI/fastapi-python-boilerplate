"""Skills router - serves the Obsidian skill library with per-user access."""
from pathlib import Path

import yaml
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..config import settings
from ..db import db
from ..security import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])


class Skill(BaseModel):
    name: str
    description: str = ""
    tags: list = []
    type: str = ""
    aliases: list = []
    body: str = ""


def _walk_skills() -> list[Path]:
    root = Path(settings.skills_dir)
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def _parse_skill(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8", errors="replace")
    body = text
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            try:
                meta = yaml.safe_load(text[3:end]) or {}
            except Exception:
                meta = {}
            body = text[end + 4:].lstrip("\n")
    return Skill(
        name=meta.get("name") or path.stem,
        description=meta.get("description", ""),
        tags=meta.get("tags") or [],
        type=meta.get("type", ""),
        aliases=meta.get("aliases") or [],
        body=body,
    )


def _allowed_skills(username: str) -> set | None:
    users = db.get("users", {})
    record = users.get(username)
    allowed = (record or {}).get("allowed_skills")
    return None if allowed is None else set(allowed)


def _filter_for_user(skills_list: list, username: str) -> list:
    allowed = _allowed_skills(username)
    if allowed is None:
        return skills_list
    return [s for s in skills_list if s.name in allowed or Path(s.name).stem in allowed]


def _authorize(username: str, skill: Skill):
    allowed = _allowed_skills(username)
    if allowed is not None and skill.name not in allowed and Path(skill.name).stem not in allowed:
        raise HTTPException(status_code=403, detail=f"not allowed to access skill '{skill.name}'")


@router.get("", response_model=list[Skill])
def list_skills(user: str = Depends(get_current_user)):
    return _filter_for_user([_parse_skill(p) for p in _walk_skills()], user)


@router.get("/search", response_model=list[Skill])
def search_skills(q: str = "", user: str = Depends(get_current_user)):
    ql = q.lower()
    out = []
    for p in _walk_skills():
        s = _parse_skill(p)
        hay = " ".join([s.name, s.description, " ".join(s.tags)]).lower()
        if ql in hay:
            out.append(s)
    return _filter_for_user(out, user)


@router.get("/{name}", response_model=Skill)
def get_skill(name: str, user: str = Depends(get_current_user)):
    for p in _walk_skills():
        s = _parse_skill(p)
        if s.name == name or p.stem == name:
            _authorize(user, s)
            return s
    raise HTTPException(status_code=404, detail=f"skill '{name}' not found")

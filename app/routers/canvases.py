from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict

from app.auth import get_current_user
from app.database import get_db
from app.models import Canvas, CanvasStatus
from app.schemas import CanvasCreate, CanvasUpdate, CanvasResponse

router = APIRouter(prefix="/api/canvases", tags=["Canvases"])

# Helper + RLS auto‑applied
async def _get_canvas(canvas_id: int, user_id: str, db: AsyncSession):
    res = await db.execute(select(Canvas).where(Canvas.id == canvas_id, Canvas.user_id == user_id))
    c = res.scalar_one_or_none()
    if not c: raise HTTPException(404, "Canvas not found")
    return c

@router.post("/", response_model=CanvasResponse, status_code=201)
async def create_canvas(data: CanvasCreate, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Create new persistent workspace"""
    canvas = Canvas(user_id=user_id, **data.model_dump(), change_log=[{"action":"created","by":user_id}])
    db.add(canvas)
    await db.commit()
    await db.refresh(canvas)
    return canvas

@router.get("/", response_model=List[CanvasResponse])
async def list_canvases(status: Optional[CanvasStatus] = None, user_id=Depends(get_current_user), db=Depends(get_db)):
    q = select(Canvas).where(Canvas.user_id == user_id).order_by(Canvas.updated_at.desc())
    if status: q = q.where(Canvas.status == status)
    return (await db.execute(q)).scalars().all()

@router.get("/{id}", response_model=CanvasResponse)
async def get_canvas(id: int, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Get full context + history"""
    return await _get_canvas(id, user_id, db)

@router.patch("/{id}", response_model=CanvasResponse)
async def update_canvas(id: int, data: CanvasUpdate, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Update state, artifacts, context — logs change"""
    c = await _get_canvas(id, user_id, db)
    update = data.model_dump(exclude_unset=True)
    update.setdefault("change_log", c.change_log + [{"action":"update","by":user_id,"at":"now"}])
    for k,v in update.items(): setattr(c,k,v)
    await db.commit(); await db.refresh(c)
    return c

@router.post("/{id}/review", response_model=CanvasResponse)
async def request_review(id: int, user_id=Depends(get_current_user), db=Depends(get_db)):
    """Steer workflow: move to human review"""
    c = await _get_canvas(id, user_id, db)
    c.status = CanvasStatus.REVIEW
    await db.commit(); return c

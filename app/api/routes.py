from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth import create_access_token, require_role, get_current_user
from app.api.streaming import sse_response
from app.models.user_models import UserCreate, UserOut, TokenOut
from app.services.users import get_repo, fanout_profile

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/users", response_model=UserOut)
async def create_user(
    data: UserCreate,
    repo=Depends(get_repo),
    background: BackgroundTasks = None,  # FastAPI injects if type hint present
):
    created = await repo.create_user(data.email)
    # Background task example
    if background is not None:
        background.add_task(lambda: None)  # replace with real job enqueue
    return {"id": created["id"], "email": created["email"], "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)}

@router.get("/profile/{user_id}")
async def profile(user_id: str):
    return await fanout_profile(user_id)

@router.get("/events")
async def events():
    return sse_response()

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user

@router.get("/admin-only")
async def admin_only(user=Depends(require_role("admin"))):
    return {"ok": True, "user": user}

# Auth endpoints (separate from /api for clarity)
auth_router = APIRouter(tags=["auth"])

@auth_router.post("/auth/token", response_model=TokenOut)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Demo only: treat username as user id; password ignored
    # In production: verify password, lookup user in DB
    subject = form.username
    role = "admin" if subject == "root" else "user"
    token = create_access_token(subject=subject, role=role)
    return TokenOut(access_token=token)

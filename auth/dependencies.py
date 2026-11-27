from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .schemas import TokenData, User
from .security import SECRET_KEY, ALGORITHM


# ──────────────────────────────────────────────
# OAuth2 Scheme
# ──────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",  # Matches your login endpoint path
    scopes={
        "me": "Access your own profile and data",
        "admin": "Full administrative access",
    },
)


# ──────────────────────────────────────────────
# Mock User Lookup — REPLACE THIS WITH YOUR DATABASE
# ──────────────────────────────────────────────
# Import your actual User model and DB session here
fake_users_db: dict[str, dict] = {}


def get_user_from_db(username: str) -> Optional[User]:
    """
    Look up a user from your database.
    🔄 REPLACE THIS with your actual database query!
    """
    user_data = fake_users_db.get(username)
    if user_data:
        return User(**user_data)
    return None


# ──────────────────────────────────────────────
# Core Auth Dependencies
# ──────────────────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency that extracts and validates the current user from JWT.
    Raises 401 if token is invalid/missing.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes: list[str] = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception

    user = get_user_from_db(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Same as get_current_user but also ensures the account is not disabled.
    Use this for most protected routes.
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


# ──────────────────────────────────────────────
# Scope-Based Permission Checks
# ──────────────────────────────────────────────
def require_scope(required_scope: str):
    """
    Create a dependency that enforces a specific scope/permission.

    Usage:
        @app.get("/admin")
        def admin_only(user = Depends(require_scope("admin"))):
            ...
    """
    async def scope_dependency(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if required_scope not in current_user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied — requires scope: '{required_scope}'"
            )
        return current_user
    return scope_dependency

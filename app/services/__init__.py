from typing import TYPE_CHECKING, Any
from .hook_service import HookService

__all__ = ["HookService"]

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .items import ItemService
    from .users import UserRepo

__all__ = ["ItemService", "UserRepo"]


def __getattr__(name: str) -> Any:
    if name == "ItemService":
        from .items import ItemService

        return ItemService
    if name == "UserRepo":
        from .users import UserRepo

        return UserRepo
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

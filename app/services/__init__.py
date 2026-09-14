"""
Service layer initialization.

Submodules are resolved lazily (PEP 562) rather than imported eagerly. Eager
imports here pulled in ``items`` -> ``app.db.repositories`` for *every* import
under ``app.services``, so a single broken module downstream made the whole
package — and anything that touches a service — unimportable.
"""

from typing import TYPE_CHECKING, Any

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

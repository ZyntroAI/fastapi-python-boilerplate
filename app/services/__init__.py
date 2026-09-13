"""Service layer package.

This module deliberately imports **nothing** at package-import time.

It previously did ``from .users import UserService`` — a class that has never
existed in this package (``users.py`` defines ``UserRepo``, ``get_repo`` and
``fanout_profile``). Because a package ``__init__`` runs before any submodule
import, that single wrong name made every ``from app.services.<x> import y``
fail, which in turn stopped ``app.main`` — the entrypoint in ``app/Dockerfile``
— from importing at all.

Consumers import the submodule they need directly::

    from app.services.token_service import create_jwt_token
    from app.services.user_service import fetch_userinfo

This mirrors ``app/__init__.py``, which carries the same policy for the same
reason.
"""

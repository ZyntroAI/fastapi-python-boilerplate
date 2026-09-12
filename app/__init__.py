"""FastAPI application package.

The application instance is defined in :mod:`app.main` and served as
``app.main:app`` (see ``app/Dockerfile``, ``Makefile``, and the deploy configs).

This module deliberately imports **nothing**. It previously created a second,
conflicting FastAPI app here and instrumented it before the object existed
(``FastAPIInstrumentor.instrument_app(app)`` on line 37 ran ahead of
``app = FastAPI(...)`` on line 43), which made ``import app`` fail outright and
took down every test collection that touched the package. It also imported
``app.routes``, a module that has never existed in this repository.

Anything that belongs at package-import time is already handled by
``app.main``; instrumentation belongs in the app's lifespan, not here.
"""

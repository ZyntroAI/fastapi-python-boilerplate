"""FastAPI entry — mounts Strawberry GraphQL at /graphql with a DB session."""
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter

from app.auth import AuthError, decode_token
from app.config import settings
from app.database import AsyncSessionLocal
from app.schema import schema


async def get_context(token: Optional[str] = None, db=None):
    context: dict = {"user": None, "db": None}
    # Strawberry context_getter may be called without db in some paths; open a session.
    if db is None:
        db = AsyncSessionLocal()
    context["db"] = db
    if token:
        try:
            context["user"] = decode_token(token)
        except AuthError:
            context["user"] = None
    return context


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    return JSONResponse(status_code=500, content={"errors": [{"message": str(exc)}], "data": None})


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "graphql-api"}

"""FastAPI entry — mounts Strawberry GraphQL at /graphql."""
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter

from app.auth import AuthError, decode_token
from app.config import settings
from app.schema import schema


async def get_context(token: Optional[str] = None):
    context: dict = {"user": None}
    if token:
        try:
            payload = decode_token(token)
            context["user"] = payload
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

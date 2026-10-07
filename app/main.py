from fastapi import FastAPI
from app.api.v1.endpoints.claude import router as claude_router
app = FastAPI(title="FastAPI + Claude Boilerplate")
# ... your existing routes ...
app.include_router(claude_router, prefix="/v1")

from fastapi import APIRouter
from .endpoints import llm, status, graph  # ✅ Import Graph

api_router = APIRouter()
api_router.include_router(llm.router, prefix="/llm", tags=["LLM"])
api_router.include_router(graph.router, prefix="/graph", tags=["LangGraph"])  # ✅ Add
api_router.include_router(status.router, tags=["System"])

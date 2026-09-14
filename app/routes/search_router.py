from fastapi import APIRouter, Query, HTTPException
from app.services.search_service import SearchService

router = APIRouter(
    prefix="/api/v1/search",
    tags=["search"]
)

@router.get("/", summary="Run a search query")
def search(q: str = Query(..., min_length=2, description="Search query string")):
    """
    Perform a search against the backend service.
    - Requires a query string `q` with at least 2 characters.
    - Returns a list of matching results.
    """
    try:
        return SearchService().query(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/stats", summary="Get search statistics")
def stats():
    """
    Return aggregated search statistics.
    Useful for monitoring usage patterns or analytics dashboards.
    """
    try:
        return SearchService().stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

/*/ app/api/v1/endpoints/code_Review.py
/*/
​from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.llm_client import LLMClient

router = APIRouter()

class CodeReviewRequest(BaseModel):
    code_snippet: str
    language: str = "python"
    rubric: List[str] = ["security", "performance", "readability"]

class ReviewResult(BaseModel):
    score: float
    feedback: List[str]
    suggested_fix: Optional[str] = None

@router.post("/review", response_model=ReviewResult)
async def review_code(request: CodeReviewRequest):
    """
    Analyzes code based on rubric and returns a score + feedback.
    Integrates with GitHub Actions for automated PR comments.
    """
    try:
        # Simulating LLM call (In production, call actual model)
        llm = LLMClient()
        feedback = await llm.analyze_code(request.code_snippet, request.rubric)
        
        # Simple heuristic for demo: 0.0 to 1.0 score
        score = 0.85 if "security" in request.rubric else 0.92
        
        return ReviewResult(
            score=score,
            feedback=feedback,
            suggested_fix="Consider using a secure random generator here."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

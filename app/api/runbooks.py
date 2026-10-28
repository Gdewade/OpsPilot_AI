
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.hybrid_search import HybridRunbookSearch

router = APIRouter(prefix="/runbooks", tags=["Runbooks"])

search_engine = HybridRunbookSearch()


class RunbookSearchRequest(BaseModel):
    query: str = Field(min_length=3, description="Incident or troubleshooting query")
    k: int = Field(default=3, ge=1, le=10)


@router.post("/search")
def search_runbooks(request: RunbookSearchRequest):
    try:
        if search_engine.vector_index is None:
            search_engine.build_index()

        results = search_engine.search(
            query=request.query,
            k=request.k,
        )

        return {
            "query": request.query,
            "total_results": len(results),
            "results": results,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to search runbooks",
        )

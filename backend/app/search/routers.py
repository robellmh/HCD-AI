"""
This module contains FastAPI routes for search.
"""

from fastapi import APIRouter, Depends

from ..auth.dependencies import authenticate_either
from .schemas import SearchResponse, UserQuery

# Use correct dependency attribute `authenticate_either`.
router = APIRouter(
    dependencies=[Depends(authenticate_either)], tags=["Search endpoints"]
)


@router.post("/search", response_model=SearchResponse)
async def search(user_query: UserQuery) -> SearchResponse:
    """
    This endpoint responds to single-turn search queries.
    """
    # Return a mock search response as a demonstration.
    return SearchResponse(response="This is a sample response")

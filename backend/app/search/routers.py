"""
This module contains FastAPI routes for search
"""

from fastapi import APIRouter, Depends

from ..auth.dependencies import authenticate_key
from .schemas import SearchResponse, UserQuery

router = APIRouter(dependencies=[Depends(authenticate_key)], tags=["Search endpoints"])


@router.post("/search")
async def search(user_query: UserQuery) -> SearchResponse:
    """
    This endpoint is used to respond to single-turn search queries
    """
    return SearchResponse(response="This is a sample response")

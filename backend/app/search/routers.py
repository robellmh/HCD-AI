"""
This module contains FastAPI routes for search
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import authenticate_key
from ..database import get_async_session
from .models import save_query
from .schemas import SearchResponse, UserQuery

router = APIRouter(dependencies=[Depends(authenticate_key)], tags=["Search endpoints"])


@router.post("/search")
async def search(
    user_query: UserQuery,
    asession: AsyncSession = Depends(get_async_session),
) -> SearchResponse:
    """
    This endpoint is used to respond to single-turn search queries
    """
    await save_query(user_query, asession)

    return SearchResponse(response="This is a sample response")

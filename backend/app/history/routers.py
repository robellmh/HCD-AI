"""
This module contains FastAPI routes for history management
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import authenticate_key
from .schemas import History, HistoryResponse, ListHistoryResponse, Response

router = APIRouter(dependencies=[Depends(authenticate_key)], tags=["History endpoints"])

# In-memory storage for history (can be replaced with a database in production)
history_storage: List[History] = []


@router.post("/history", response_model=HistoryResponse)
async def create_history(
    chat_id: UUID, created_by: str, responses: List[Response]
) -> HistoryResponse:
    """
    This endpoint creates a history entry for a chat
    """
    history = History(
        chat_id=chat_id,
        created_by=created_by,
        responses=responses,
    )
    history_storage.append(history)  # Save history in the in-memory storage
    return HistoryResponse(history=history)


@router.get("/history/{chat_id}", response_model=HistoryResponse)
async def get_history_by_chat_id(chat_id: UUID) -> HistoryResponse:
    """
    This endpoint retrieves history by chat_id
    """
    for history in history_storage:
        if history.chat_id == chat_id:
            return HistoryResponse(history=history)
    raise HTTPException(
        status_code=404, detail="History not found for the given chat ID"
    )


@router.get("/history/user/{created_by}", response_model=ListHistoryResponse)
async def get_history_by_created_by(created_by: str) -> ListHistoryResponse:
    """
    This endpoint retrieves a list of history entries created by a specific user
    """
    user_histories = [
        history for history in history_storage if history.created_by == created_by
    ]
    return ListHistoryResponse(histories=user_histories)

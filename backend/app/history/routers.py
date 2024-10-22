"""
This module contains FastAPI routes for history management
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import authenticate_key
from .schemas import (
    History,
    HistoryResponse,
    ListHistoryResponse,
)

router = APIRouter(dependencies=[Depends(authenticate_key)], tags=["History endpoints"])

# In-memory storage for history (can be replaced with a database in production)
history_storage: List[History] = []


@router.post("/history", response_model=HistoryResponse)
async def create_history(chat_history: History) -> HistoryResponse:
    """
    This endpoint creates a history entry for a chat
    """
    history_storage.append(chat_history)  # Save history in the in-memory storage
    return HistoryResponse(history=chat_history)


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

    if len(user_histories) == 0:
        raise HTTPException(
            status_code=404, detail="History not found for the given user"
        )

    return ListHistoryResponse(histories=user_histories)

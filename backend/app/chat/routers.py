"""
This module contains FastAPI routes for chat
"""

from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import get_current_user
from .schemas import (
    AskQuestionRequest,
    AskResponse,
    Chat,
    ChatDetailResponse,
    ChatResponse,
    NewChatRequest,
)

router = APIRouter(dependencies=[Depends(get_current_user)], tags=["Chat endpoints"])

# In-memory storage for chats (can be replaced with a database in production)
chats: Dict[UUID, Chat] = {}


@router.post("/chat", response_model=ChatResponse)
async def start_chat(new_chat_request: NewChatRequest) -> ChatResponse:
    """
    This endpoint is used to start a new chat
    """
    chat = Chat(
        user_name=new_chat_request.user_name,
        created_date_time=new_chat_request.created_date_time,
    )
    chats[chat.chat_id] = chat  # Save chat in the in-memory storage
    return ChatResponse(response=f"Chat started successfully with ID: {chat.chat_id}")


@router.get("/chat/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(chat_id: UUID) -> ChatDetailResponse:
    """
    This endpoint retrieves a chat by chat_id
    """
    chat = chats.get(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatDetailResponse(chat=chat)


@router.post("/chat/{chat_id}/ask", response_model=AskResponse)
async def ask_question(chat_id: UUID, ask_request: AskQuestionRequest) -> AskResponse:
    """
    This endpoint allows the user to ask a question in the chat
    """
    chat = chats.get(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Simulate processing the question and generating a response
    answer = (
        f"Answer to your question '{ask_request.question}': "
        "[Simulated answer based on business logic here]"
    )

    return AskResponse(answer=answer)

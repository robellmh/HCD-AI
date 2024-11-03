"""
This module contains FastAPI routes for chat
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import authenticate_key
from ..database import get_async_session
from ..ingestion.models import get_similar_n_chunks
from ..llm_utils.completion import get_llm_response
from ..llm_utils.embeddings import create_embeddings
from .schemas import (
    ChatHistory,
    ChatResponse,
    ChatUserMessage,
)

router = APIRouter(dependencies=[Depends(authenticate_key)], tags=["Chat endpoints"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatUserMessage, asession: AsyncSession = Depends(get_async_session)
) -> ChatResponse:
    """
    This is the endpoint called for chat
    """
    # Get embeddings for message
    # Get Top N similar messages
    # Send Top N similar messages to LLM to get response
    # Return response
    message_embeddings = await create_embeddings(chat_request.message)
    similar_chunks = await get_similar_n_chunks(
        message_embeddings, n_similar=5, asession=asession
    )
    llm_response = await get_llm_response(
        user_message=chat_request.message, similar_chunks=similar_chunks
    )

    return ChatResponse(
        response=llm_response.answer,
        chat_id=chat_request.chat_id,
        response_metadata=similar_chunks,
    )


@router.get("/chat/{session_id}", response_model=ChatHistory)
async def get_chat(session_id: UUID) -> ChatHistory:
    """
    This endpoint retrieves a chat by chat_id
    """

    return []

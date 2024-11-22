"""
This module contains FastAPI routes for chat
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import authenticate_key
from ..config import USE_CROSS_ENCODER
from ..database import get_async_session
from ..services.ChatService import ChatService
from ..services.DocumentService import DocumentService
from ..services.utils.completion import (
    get_llm_response,
)
from ..services.utils.embeddings import create_embeddings
from .config import N_TOP_CONTENT, N_TOP_RERANK
from .models import save_chat_request, save_chat_response
from .schemas import (
    ChatHistory,
    ChatResponse,
    ChatResponseBase,
    ChatUserMessageBase,
)

router = APIRouter(dependencies=[Depends(authenticate_key)], tags=["Chat endpoints"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatUserMessageBase,
    request: Request,
    asession: AsyncSession = Depends(get_async_session),
) -> ChatResponse:
    """
    This is the endpoint called for chat. Note that it is currently just a single turn
    and does not retrieve chat history.
    """

    chat_request = await ChatService.update_request_using_history(
        chat_request, asession
    )
    saved_chat_request = await save_chat_request(chat_request, asession)

    message_embeddings = await create_embeddings(chat_request.message)
    similar_chunks = await DocumentService.get_similar_n_chunks(
        message_embeddings, n_similar=N_TOP_CONTENT, asession=asession
    )
    if USE_CROSS_ENCODER == "True" and (N_TOP_RERANK > N_TOP_CONTENT):
        raise ValueError(
            (
                "N_TOP_RERANK should be less than or equal to N_TOP_CONTENT "
                "when using cross-encoder"
            )
        )

    if USE_CROSS_ENCODER == "True" and len(similar_chunks) > 1:
        similar_chunks = await DocumentService.rerank_chunks(
            query_text=chat_request.message,
            similar_chunks=similar_chunks,
            request=request,
            n_top_rerank=N_TOP_RERANK,
        )
    llm_response = await get_llm_response(
        user_message=chat_request.message,
        session_summary=chat_request.session_summary or "",
        similar_chunks=similar_chunks,
    )

    chat_response_base = ChatResponseBase(
        response=llm_response.answer,
        request_id=saved_chat_request.request_id,
        chat_id=saved_chat_request.chat_id,
        response_metadata={
            i: chunk.model_dump() for i, chunk in similar_chunks.items()
        },
    )

    saved_chat_response = await save_chat_response(chat_response_base, asession)
    chat_response = ChatResponse.model_validate(saved_chat_response)

    return chat_response


@router.get("/chat/{chat_id}", response_model=ChatHistory)
async def get_chat(
    chat_id: str,
    asession: AsyncSession = Depends(get_async_session),
) -> ChatHistory:
    """
    This endpoint retrieves a chat by chat_id
    """

    chats = await ChatService.get_chat_history(str(chat_id), asession)

    if not chats:
        raise HTTPException(status_code=404, detail=f"Session id: {chat_id} not found")
    return chats

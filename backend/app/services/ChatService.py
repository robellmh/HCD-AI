from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..chat.models import ChatRequestDB, ChatResponseDB
from ..chat.schemas import (
    ChatHistory,
    ChatResponse,
    ChatUserMessage,
    ChatUserMessageBase,
    ChatUserMessageRefined,
)
from .utils.completion import get_refined_message, get_session_summary


class ChatService:
    """
    Service class for handling chat requests
    """

    @staticmethod
    async def update_request_using_history(
        chat_request: ChatUserMessageBase, asession: AsyncSession
    ) -> ChatUserMessageRefined:
        """
        Update chat request using history.

        """

        chat_request_refined = ChatUserMessageRefined.model_validate(chat_request)
        chat_history = await ChatService.get_chat_history(
            chat_request.chat_id, asession
        )
        if chat_history:
            session_summary = await get_session_summary(
                chat_history, chat_request.message
            )
            refined_message = await get_refined_message(
                session_summary, chat_request.message
            )
            chat_request_refined.message_original = chat_request.message
            chat_request_refined.message = refined_message
            chat_request_refined.session_summary = session_summary

        return chat_request_refined

    @staticmethod
    async def get_chat_history(
        chat_id: str | None, asession: AsyncSession
    ) -> ChatHistory:
        """
        Get chat history for a chat.

        Note: At present it is only retrieving it from Db. To make it
        more performant, we can cache the chat history in redis.
        """
        if chat_id is None:
            return []

        stmt_requests = (
            select(ChatRequestDB)
            .where(ChatRequestDB.chat_id == chat_id)
            .order_by(ChatRequestDB.created_datetime_utc)
        )

        chat_requests_db = (await asession.execute(stmt_requests)).scalars().all()
        chat_requests = [ChatUserMessage.model_validate(c) for c in chat_requests_db]

        stmt_responses = (
            select(ChatResponseDB)
            .join(ChatRequestDB)
            .where(ChatRequestDB.chat_id == chat_id)
            .order_by(
                ChatResponseDB.created_datetime_utc,
            )
        )

        chat_responses_db = (await asession.execute(stmt_responses)).scalars().all()
        chat_responses = [ChatResponse.model_validate(c) for c in chat_responses_db]

        return sorted(
            [*chat_requests, *chat_responses], key=lambda x: x.created_datetime_utc
        )

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base, JSONDict
from .schemas import (
    ChatResponseBase,
    ChatUserMessageRefined,
)


class ChatRequestDB(Base):
    """ORM for chat requests"""

    __tablename__ = "chat_requests"

    request_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[str] = mapped_column(String, nullable=False)
    created_datetime_utc: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    user_id: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String)
    message_original: Mapped[str] = mapped_column(String, nullable=True)
    session_summary: Mapped[str] = mapped_column(String, nullable=True)
    response: Mapped["ChatResponseDB"] = relationship(
        "ChatResponseDB", back_populates="request"
    )


class ChatResponseDB(Base):
    """ORM for chat responses"""

    __tablename__ = "chat_responses"

    response_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chat_requests.request_id")
    )
    created_datetime_utc: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    response: Mapped[str] = mapped_column(String)
    response_metadata: Mapped[JSONDict] = mapped_column(JSON, nullable=True)

    request: Mapped["ChatRequestDB"] = relationship(
        "ChatRequestDB", back_populates="response"
    )
    chat_id: Mapped[str] = mapped_column(String, nullable=False)


async def save_chat_request(
    chat_request: ChatUserMessageRefined, asession: AsyncSession
) -> ChatRequestDB:
    """Save chat request to database"""

    chat_request_db = ChatRequestDB(
        chat_id=chat_request.chat_id or str(uuid4()),
        user_id=chat_request.user_id,
        message=chat_request.message,
        message_original=chat_request.message_original,
        session_summary=chat_request.session_summary,
    )
    asession.add(chat_request_db)
    await asession.commit()
    return chat_request_db


async def save_chat_response(
    chat_response: ChatResponseBase, asession: AsyncSession
) -> ChatResponseDB:
    """Save chat response to database"""
    chat_response_db = ChatResponseDB(
        request_id=chat_response.request_id,
        response=chat_response.response,
        response_metadata=chat_response.response_metadata,
        chat_id=chat_response.chat_id,
    )
    asession.add(chat_response_db)
    await asession.commit()
    return chat_response_db

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatUserMessageBase(BaseModel):
    """
    Schema for a user's chat message
    """

    chat_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    message: str
    model_config = ConfigDict(from_attributes=True)


class ChatUserMessageRefined(ChatUserMessageBase):
    """
    Schema for a user's chat message with refined fields
    """

    message_original: Optional[str] = None
    session_summary: Optional[str] = None


class ChatUserMessage(ChatUserMessageRefined):
    """
    Schema for a user's chat message
    """

    request_id: int
    created_datetime_utc: datetime


class ChatResponseBase(BaseModel):
    """
    Schema for the response to a user's chat message
    """

    response: str = Field(
        ...,
        examples=["This is a sample chat response"],
    )
    request_id: int
    response_metadata: Optional[dict] = Field(
        default_factory=lambda: {},
        examples=[{"timestamp": "2024-10-16T12:31:00Z"}],
    )
    chat_id: str
    model_config = ConfigDict(from_attributes=True)


class ChatResponse(ChatResponseBase):
    """
    Schema for the response to a user's chat message
    """

    response_id: int
    created_datetime_utc: datetime


ChatHistory = list[ChatResponse | ChatUserMessage]

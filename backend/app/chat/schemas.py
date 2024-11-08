from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatUserMessageBase(BaseModel):
    """
    Schema for a user's chat message
    """

    session_id: Optional[str] = None
    user_id: int
    message: str

    model_config = ConfigDict(from_attributes=True)


class ChatUserMessage(ChatUserMessageBase):
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
        default_factory=dict, examples=[{"timestamp": "2024-10-16T12:31:00Z"}]
    )

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(ChatResponseBase):
    """
    Schema for the response to a user's chat message
    """

    response_id: int
    created_datetime_utc: datetime


ChatHistory = list[ChatResponse | ChatUserMessage]

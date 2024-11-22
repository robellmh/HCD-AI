from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class NewChatRequest(BaseModel):
    """
    Schema for starting a new chat
    """

    user_name: str = Field(..., examples=["John Doe"])
    created_date_time: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class Chat(BaseModel):
    """
    Schema for a Chat
    """

    chat_id: UUID = Field(default_factory=uuid4)
    user_name: str
    created_date_time: datetime

    model_config = ConfigDict(from_attributes=True)


class AskQuestionRequest(BaseModel):
    """
    Schema for asking a question
    """

    question: str = Field(..., examples=["What are the symptoms of diabetes?"])

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    """
    Schema for the response to a user's chat message
    """

    response: str = Field(
        ...,
        examples=["This is a sample chat response"],
    )
    response_metadata: Optional[dict] = Field(
        default_factory=lambda: {},  # Fixed for mypy compatibility
        examples=[{"timestamp": "2024-10-16T12:31:00Z"}],
    )


class AskResponse(BaseModel):
    """
    Schema for the response to a user's question
    """

    answer: str = Field(
        ...,
        examples=[
            "The symptoms of diabetes include increased thirst, "
            "frequent urination, and fatigue."
        ],
    )


class ChatDetailResponse(BaseModel):
    """
    Schema for the detailed response of a chat
    """

    chat: Chat

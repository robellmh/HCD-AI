from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ChatUserMessage(BaseModel):
    """
    Schema for a user's chat message
    """

    chat_id: UUID = Field(default_factory=uuid4)
    session_id: Optional[str] = None
    user_id: int
    message: str

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    """
    Schema for the response to a user's chat message
    """

    response: str = Field(
        ...,
        examples=["This is a sample chat response"],
    )
    chat_id: UUID

    response_metadata: Optional[dict] = Field(
        default_factory=dict, examples=[{"timestamp": "2024-10-16T12:31:00Z"}]
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


ChatHistory = list[ChatResponse | ChatUserMessage]

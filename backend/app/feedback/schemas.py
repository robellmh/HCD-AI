from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Feedback(BaseModel):
    """
    Schema for user feedback
    """

    feedback_id: UUID = Field(default_factory=uuid4)
    user_name: str
    chat_id: UUID
    feedback_text: str
    like: bool
    created_datetime: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class FeedbackRequest(BaseModel):
    """
    Pydantic model for feedback submission
    """

    user_name: str
    chat_id: str
    feedback_text: str
    like: bool


class FeedbackResponse(BaseModel):
    """
    Schema for the response when retrieving feedback
    """

    feedback: Feedback


class ListFeedbackResponse(BaseModel):
    """
    Schema for the response when retrieving a list of feedback entries
    """

    feedbacks: List[Feedback]

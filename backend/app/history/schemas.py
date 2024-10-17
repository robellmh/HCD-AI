from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Response(BaseModel):
    """
    Schema for a single response in the history
    """

    question: str
    answer: str


class History(BaseModel):
    """
    Schema for a History entry
    """

    history_id: UUID = Field(default_factory=uuid4)
    chat_id: UUID
    responses: List[Response] = Field(default_factory=list)
    created_by: str
    created_datetime: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class HistoryResponse(BaseModel):
    """
    Schema for the response when retrieving history
    """

    history: History


class ListHistoryResponse(BaseModel):
    """
    Schema for the response when retrieving a list of history entries
    """

    histories: List[History]

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserQuery(BaseModel):
    """
    Schema for a User Query
    """

    query_text: str = Field(..., examples=["How should I check for Jaundice?"])
    query_metadata: Optional[dict] = Field(
        default_factory=lambda: {}, examples=[{"age": "0.5"}]
    )

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    """
    Schema for the response to a user's query
    """

    response: str = Field(
        ...,
        examples=[
            "You should check for Jaundice by checking for yellow eyes and feet."
        ],
    )
    response_metadata: Optional[dict] = Field(
        default_factory=lambda: {}, examples=[{"age": "0.5"}]
    )

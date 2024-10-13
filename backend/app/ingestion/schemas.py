"""This module contains the Pydantic models (schemas) for data validation and
serialization."""

from pydantic import BaseModel


class IngestionResponse(BaseModel):
    """Pydantic model for the response of the ingestion endpoint."""

    file_name: str
    file_id: str

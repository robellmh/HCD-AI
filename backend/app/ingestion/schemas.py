"""This module contains the Pydantic models (schemas) for data validation and
serialization."""

from datetime import datetime

from pydantic import BaseModel


class IngestionResponse(BaseModel):
    """Pydantic model for the response of the ingestion endpoint."""

    file_name: str
    file_id: str
    total_chunks: int


class DocumentInfo(BaseModel):
    """Pydantic model for the document information."""

    file_id: str
    file_name: str
    total_chunks: int
    created_datetime_utc: datetime
    updated_datetime_utc: datetime
    is_archived: bool


class DocumentInfoList(BaseModel):
    """Pydantic model for the list of documents."""

    documents: list[DocumentInfo]


class DocumentChunk(BaseModel):
    """Pydantic model for a document."""

    file_name: str
    chunk_id: int
    text: str
    distance: float

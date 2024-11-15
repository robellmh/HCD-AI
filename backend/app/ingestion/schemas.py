"""This module contains the Pydantic models (schemas) for data validation and
serialization."""

from typing import Optional

from pydantic import BaseModel


class IngestionResponse(BaseModel):
    """Pydantic model for the response of the ingestion endpoint."""

    file_name: str
    file_id: str
    total_chunks: int


class DocumentChunk(BaseModel):
    """Pydantic model for a document."""

    file_name: str
    chunk_id: int
    text: str
    distance: float
    rerank_score: Optional[float] = None

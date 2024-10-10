"""This module contains the Pydantic models (schemas) for data validation and
serialization."""

from datetime import datetime

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    file_name: str
    content: bytes


class Document(BaseModel):
    file_name: str
    chunk_id: int
    text: str
    created_datetime_utc: datetime
    updated_datetime_utc: datetime


class DocumentChunk(BaseModel):
    chunk_id: int
    text: str


class DocumentResponse(BaseModel):
    status: str
    message: str
    document_ids: list[int]

"""This module contains the Pydantic models (schemas) for data validation and
serialization."""

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    file_name: str
    content: bytes


class Document(BaseModel):
    uuid: UUID
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
    document_ids: List[UUID]

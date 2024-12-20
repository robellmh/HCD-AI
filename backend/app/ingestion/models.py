"""This module contains the ORM for managing documents in the database and
database helper functions such as saving, updating, deleting, and retrieving documents.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from numpy import ndarray
from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ..config import (
    PGVECTOR_DISTANCE,
    PGVECTOR_EF_CONSTRUCTION,
    PGVECTOR_M,
    PGVECTOR_VECTOR_SIZE,
)
from ..models import Base
from ..utils import setup_logger

logger = setup_logger()


class DocumentDB(Base):
    """ORM for managing document indexing."""

    __tablename__ = "documents"

    __table_args__ = (
        Index(
            "documents_embedding_idx",
            "embedding_vector",
            postgresql_using="hnsw",
            postgresql_with={
                "M": PGVECTOR_M,
                "ef_construction": PGVECTOR_EF_CONSTRUCTION,
            },
            postgresql_ops={"embedding": PGVECTOR_DISTANCE},
        ),
    )

    content_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

    file_name: Mapped[str] = mapped_column(String(length=150), nullable=False)
    file_id: Mapped[str] = mapped_column(String(length=36), nullable=False)
    chunk_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_vector: Mapped[Vector] = mapped_column(
        Vector(int(PGVECTOR_VECTOR_SIZE)), nullable=False
    )
    created_datetime_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_datetime_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=datetime.now(timezone.utc), nullable=False
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


async def save_document_to_db(
    *,
    text_embeddings: list[tuple[str, ndarray]],
    file_name: str,
    asession: AsyncSession,
) -> str:
    """
    Save documents to the database.

    Parameters
    ----------
    text_embeddings
        A list of tuples. Each tuple is a pair of text and its embedding.
    file_name
        The name of the file from which the text was extracted
    asession
        AsyncSession object for database transactions.

    Returns
    -------
    str
        The file_id of the saved document.
    """

    documents = []
    file_id = str(uuid.uuid4())
    for chunk_id, (text, embedding_vector) in enumerate(text_embeddings):
        document = DocumentDB(
            file_name=file_name,
            file_id=file_id,
            chunk_id=chunk_id,
            text=text,
            embedding_vector=embedding_vector,
            created_datetime_utc=datetime.now(timezone.utc),
            updated_datetime_utc=datetime.now(timezone.utc),
        )
        documents.append(document)

    asession.add_all(documents)
    await asession.commit()
    await asession.rollback()

    return file_id


async def get_document_from_db(
    *,
    content_id: int,
    asession: AsyncSession,
) -> Optional[DocumentDB]:
    """
    Retrieve a document from the database.

    Parameters
    ----------
    content_id
        The content_id of the document to retrieve.
    asession
        AsyncSession object for database transactions.

    Returns
    -------
    Optional[DocumentDB]
        The DocumentDB instance if found, else None.
    """
    return await asession.get(DocumentDB, content_id)

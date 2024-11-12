"""This module contains the ORM for managing documents in the database and
database helper functions such as saving, updating, deleting, and retrieving documents.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi.requests import Request
from numpy import ndarray
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Index, Integer, String, Text, select
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
from .schemas import DocumentChunk

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


async def get_similar_n_chunks(
    embeddings: ndarray, n_similar: int, asession: AsyncSession
) -> dict[int, DocumentChunk]:
    """
    Retrieve the n closest documents to the given embedding.

    Parameters
    ----------
    embeddings
        The embedding for which to find the closest documents.
    n_similar
        The number of closest documents to retrieve.
    asession
        AsyncSession object for database transactions.

    Returns
    -------
    dict[int, DocumentChunk]
        A dictionary containing the closest document chunks.
    """

    distance = DocumentDB.embedding_vector.cosine_distance(embeddings).label("distance")
    query = select(DocumentDB, distance).order_by(distance).limit(n_similar)
    search_results = (await asession.execute(query)).all()

    results_dict = {}
    for i, r in enumerate(search_results):
        results_dict[i] = DocumentChunk(
            file_name=r[0].file_name,
            chunk_id=r[0].chunk_id,
            text=r[0].text,
            distance=r[1],
        )

    return results_dict


async def rerank_chunks(
    similar_chunks: dict[int, DocumentChunk],
    query_text: str,
    n_top_rerank: int,
    request: Request,
) -> dict[int, DocumentChunk]:
    """
    This function reranks the chunks using the cross-encoder
    """
    encoder = request.app.state.crossencoder
    contents = similar_chunks.values()
    scores = encoder.predict([(query_text, content.text) for content in contents])

    sorted_by_score = [v for _, v in sorted(zip(scores, contents), reverse=True)][
        :n_top_rerank
    ]

    return dict(enumerate(sorted_by_score))

"""This module contains the ORM for managing documents in the database and
database helper functions such as saving, updating, deleting, and retrieving documents.
"""

from datetime import datetime, timezone
from io import BytesIO
from typing import List, Optional


from pgvector.sqlalchemy import Vector
from ..models import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    String,
    Text
)
from sqlalchemy.ext.asyncio import AsyncSession

import PyPDF2

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from ..config import (
                      PGVECTOR_VECTOR_SIZE,
                      EMBEDDING_MODEL_NAME,
                      PGVECTOR_M,
                      PGVECTOR_EF_CONSTRUCTION,
                      PGVECTOR_DISTANCE
)

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

    content_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        String(length=150),
        nullable=False
    )
    chunk_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    embedding_vector: Mapped[Vector] = mapped_column(
        Vector(int(PGVECTOR_VECTOR_SIZE)),
        nullable=False
    )
    created_datetime_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    updated_datetime_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=datetime.now(timezone.utc),
        nullable=False
    )


async def save_document_to_db(
    *,
    documents: List[DocumentDB],
    asession: AsyncSession,
) -> None:
    """Save documents to the database.

    Parameters
    ----------
    documents
        A list of DocumentDB instances to save.
    asession
        AsyncSession object for database transactions.
    """
    try:
        asession.add_all(documents)
        await asession.commit()
    except Exception as e:
        await asession.rollback()
        logger.error(f"Error saving documents to the database: {e}")
        raise e


async def get_document_from_db(
    *,
    content_id: int,
    asession: AsyncSession,
) -> Optional[DocumentDB]:
    """Retrieve a document from the database.

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


async def parse_file(file: bytes) -> List[str]:
    """Parse the content of an uploaded file into chunks.

    For PDFs, each page is treated as its own chunk.
    For text files, the content is split into chunks of fixed size.

    Parameters
    ----------
    file : bytes
        The content of the uploaded file.

    Returns
    -------
    List[str]
        A list of text chunks extracted from the file.
    """
    # Check if the file is a PDF
    if file[:5] == b"%PDF-":
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file))
            chunks = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    chunks.append(page_text.strip())
            if not chunks:
                raise Exception(
                    "No text could be extracted from the uploaded PDF file."
                )
        except Exception as e:
            raise Exception(f"Failed to parse PDF file: {e}")
    else:
        # Assume it's text
        try:
            text = file.decode("utf-8")
            if not text.strip():
                raise Exception(
                    "No text could be extracted from the uploaded text file."
                )
            chunk_size = 1000
            chunks = [text[i: i + chunk_size] for i in range(0, len(text), chunk_size)]
        except UnicodeDecodeError:
            raise Exception("File must be a UTF-8 encoded text file.")

    return chunks


async def create_embeddings(chunks: List[str]) -> List[List[float]]:
    """Create embeddings for a list of text chunks using HuggingFaceEmbedding
    with batch processing.

    Parameters
    ----------
    chunks
        A list of text chunks.

    Returns
    -------
    List[List[float]]
        A list of embedding vectors corresponding to each text chunk.
    """
    # Initialize the embedding model
    embed_model = HuggingFaceEmbedding(
        model_name=EMBEDDING_MODEL_NAME,
        embed_batch_size=16,
        device="cpu",
        trust_remote_code=True,
    )

    try:
        logger.info(
            f"""Generating embeddings for {len(chunks)} chunks using
                    async batch processing"""
        )
        embeddings = await embed_model.aget_text_embedding_batch(chunks)
        logger.info("Embeddings generated successfully")
    except Exception as e:
        logger.error(f"Embedding failed: {str(e)}")
        raise Exception(f"Embedding failed: {str(e)}")

    return embeddings

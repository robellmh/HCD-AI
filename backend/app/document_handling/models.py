"""This module contains the ORM for managing documents in the database and
database helper functions such as saving, updating, deleting, and retrieving documents.
"""

from datetime import datetime, timezone
from io import BytesIO
from typing import List, Optional
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from ..models import Base
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

import PyPDF2

from llama_index.embeddings.huggingface import HuggingFaceEmbedding 

from ..config import PGVECTOR_VECTOR_SIZE, EMBEDDING_MODEL_NAME
from ..utils import setup_logger


logger = setup_logger()


class DocumentDB(Base):
    """ORM for managing documents."""

    __tablename__ = "documents"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    file_name = Column(String(length=255), nullable=False)
    chunk_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding_vector = Column(Vector(int(PGVECTOR_VECTOR_SIZE)), nullable=False)
    created_datetime_utc = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    updated_datetime_utc = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of the DocumentDB object."""
        return (
            f"DocumentDB(uuid={self.uuid}, file_name={self.file_name}, "
            f"chunk_id={self.chunk_id}, created_datetime_utc={self.created_datetime_utc})"
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
    uuid: str,
    asession: AsyncSession,
) -> Optional[DocumentDB]:
    """Retrieve a document from the database.

    Parameters
    ----------
    uuid
        The UUID of the document to retrieve.
    asession
        AsyncSession object for database transactions.

    Returns
    -------
    Optional[DocumentDB]
        The DocumentDB instance if found, else None.
    """
    return await asession.get(DocumentDB, uuid)


async def parse_file(file: bytes) -> List[str]:
    """Parse the content of an uploaded file into chunks.

    Parameters
    ----------
    file : bytes
        The content of the uploaded file.

    Returns
    -------
    List[str]
        A list of text chunks extracted from the file.
    """
    text = ""

    # Check if the file is a PDF by inspecting the magic number
    if file[:5] == b'%PDF-':
        # Handle PDF files
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file))
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        except Exception as e:
            raise Exception(f"Failed to parse PDF file: {e}")
    else:
        # Assume it's a text file
        try:
            text = file.decode('utf-8')
        except UnicodeDecodeError:
            raise Exception("File must be a UTF-8 encoded text file.")

    if not text.strip():
        raise Exception("No text could be extracted from the uploaded file.")

    # Split the text into chunks
    chunk_size = 1000  # Adjust chunk size as needed
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
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
        logger.info(f"""Generating embeddings for {len(chunks)} chunks using 
                    async batch processing""")
        embeddings = await embed_model.aget_text_embedding_batch(chunks)
        logger.info("Embeddings generated successfully")
        # Check if embeddings are in the correct format
        if not isinstance(embeddings, list):
            raise Exception("Embeddings are not a list")
        if not all(isinstance(e, list) for e in embeddings):
            raise Exception("Embeddings are not a list of lists")
        if not all(isinstance(v, float) for e in embeddings for v in e):
            raise Exception("Embeddings contain non-float values")

    except Exception as e:
        logger.error(f"Embedding failed: {str(e)}")
        raise Exception(f"Embedding failed: {str(e)}")

    return embeddings

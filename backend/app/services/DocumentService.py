from datetime import datetime, timezone
from io import BytesIO
from typing import List, Optional
from uuid import uuid4

import PyPDF2
from numpy import ndarray
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import EMBEDDING_MODEL_NAME
from ..ingestion.models import DocumentDB
from ..utils import setup_logger

logger = setup_logger()


class DocumentService:
    """
    Service class for handling document ingestion and retrieval.
    """

    @staticmethod
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
        if file[:5] == b"%PDF-":
            pdf_reader = PyPDF2.PdfReader(BytesIO(file))
            chunks = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    chunks.append(page_text.strip())
            if not chunks:
                raise RuntimeError(
                    "No text could be extracted from the uploaded PDF file."
                )

        else:
            # Assume it's text
            text = file.decode("utf-8")
            if not text.strip():
                raise RuntimeError(
                    "No text could be extracted from the uploaded text file."
                )
            chunk_size = 1000
            chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

        return chunks

    @staticmethod
    async def save_document(
        text_embeddings: List[tuple[str, ndarray]],
        file_name: str,
        session: AsyncSession,
    ) -> str:
        """
        Save document embeddings to the database.

        Parameters
        ----------
        text_embeddings : List[Tuple[str, ndarray]]
            A list of tuples where each tuple has text and its embedding vector.
        file_name : str
            The name of the document file.
        session : AsyncSession
            The async session for database interaction.

        Returns
        -------
        str
            The unique file_id generated for the saved document.
        """
        documents = []
        file_id = str(uuid4())
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

        session.add_all(documents)
        await session.commit()
        await session.rollback()
        return file_id

    @staticmethod
    async def get_document(
        content_id: int, session: AsyncSession
    ) -> Optional[DocumentDB]:
        """
        Retrieve a document by content_id.
        """
        return await session.get(DocumentDB, content_id)

    @staticmethod
    async def create_embeddings(chunks: list[str]) -> ndarray:
        """
        Create embeddings for a list of text chunks using `sentence_transformers`

        Parameters
        ----------
        chunks
            A list of text chunks.

        Returns
        -------
        ndarray
            A list of embedding vectors corresponding to each text chunk.
        """

        embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME, trust_remote_code=True)

        logger.info(
            f"""Generating embeddings for {len(chunks)} chunks using
                    async batch processing"""
        )
        embeddings = embed_model.encode(chunks)
        logger.info("Embeddings generated successfully")

        return embeddings

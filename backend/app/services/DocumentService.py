from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from numpy import ndarray
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select

from ..ingestion.models import DocumentDB
from ..ingestion.schemas import DocumentInfo, DocumentInfoList
from ..services.utils.embeddings import create_embeddings
from ..services.utils.parse_file import parse_file
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
        return await parse_file(file)

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
        return await create_embeddings(chunks)

    @staticmethod
    async def list_all_docs(
        session: AsyncSession,
    ) -> DocumentInfoList:
        """
        List all documents in the database, only returning the name of the file,
        the total number of chunks associated with it, when it was uploaded,
        and when it was last updated.
        """
        query = select(
            DocumentDB.file_id,
            DocumentDB.file_name,
            DocumentDB.is_archived,
            func.count(DocumentDB.chunk_id).label("total_chunks"),
            func.min(DocumentDB.created_datetime_utc).label("created_datetime_utc"),
            func.max(DocumentDB.updated_datetime_utc).label("updated_datetime_utc"),
        ).group_by(
            DocumentDB.file_id,
            DocumentDB.file_name,
            DocumentDB.is_archived,
        )

        result = await session.execute(query)
        rows = result.fetchall()

        documents = [
            DocumentInfo(
                file_id=row.file_id,
                file_name=row.file_name,
                is_archived=row.is_archived,
                total_chunks=row.total_chunks,
                created_datetime_utc=row.created_datetime_utc,
                updated_datetime_utc=row.updated_datetime_utc,
            )
            for row in rows
        ]

        return DocumentInfoList(documents=documents)

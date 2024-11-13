from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from numpy import ndarray
from sqlalchemy.ext.asyncio import AsyncSession

from ..ingestion.models import DocumentDB


class DocumentService:
    """
    Service class for handling document ingestion and retrieval.
    """

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

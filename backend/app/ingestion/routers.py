"""This module contains the FastAPI router for the document handling endpoints."""

from io import BytesIO

import PyPDF2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from numpy import ndarray
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import EMBEDDING_MODEL_NAME
from ..database import get_async_session
from ..utils import setup_logger
from .models import save_document_to_db
from .schemas import IngestionResponse

logger = setup_logger()

TAG_METADATA = {
    "name": "Document Ingestion",
    "description": "Endpoints for ingesting documents.",
}

router = APIRouter(prefix="/ingestion", tags=[TAG_METADATA["name"]])


@router.post("/document_upload", response_model=IngestionResponse)
async def upload_document(
    file: UploadFile = File(...),
    asession: AsyncSession = Depends(get_async_session),
) -> IngestionResponse:
    """
    Upload a document, chunk it, embed each chunk,
    and store embeddings in PostgreSQL using pgvector.
    """
    file_name = file.filename or "unknown filename"

    try:
        content = await file.read()
        chunks = await parse_file(content)
        logger.info("Document parsed successfully.")

        embeddings = await create_embeddings(chunks)
        logger.info(
            f"All chunks embedded successfully. Total chunks: {len(embeddings)}"
        )

        file_id = await save_document_to_db(
            text_embeddings=list(zip(chunks, embeddings)),
            file_name=file_name,
            asession=asession,
        )

    except Exception as e:
        logger.error(f"Failed to index uploaded file: {e}")
        raise HTTPException(
            status_code=400, detail="Failed to index uploaded file."
        ) from e

    return IngestionResponse(
        file_name=file_name,
        file_id=file_id,
    )


async def parse_file(file: bytes) -> list[str]:
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
            raise RuntimeError("No text could be extracted from the uploaded PDF file.")

    else:
        # Assume it's text
        text = file.decode("utf-8")
        if not text.strip():
            raise Exception("No text could be extracted from the uploaded text file.")
        chunk_size = 1000
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    return chunks


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

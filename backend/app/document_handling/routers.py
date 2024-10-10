"""This module contains the FastAPI router for the document handling endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session
from ..utils import setup_logger
from .models import (
    DocumentDB,
    create_embeddings,
    parse_file,
    save_document_to_db,
)
from .schemas import DocumentResponse

logger = setup_logger()

TAG_METADATA = {
    "name": "Document Management",
    "description": "Endpoints for handling documents.",
}

router = APIRouter(prefix="/document_handling", tags=[TAG_METADATA["name"]])


@router.post("/document_upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    asession: AsyncSession = Depends(get_async_session),
) -> DocumentResponse:
    """
    Upload a document, process it into chunks, embed each chunk,
    and store embeddings in PostgreSQL using pgvector.
    """
    file_name = file.filename

    # Read the content of the uploaded file
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Error reading the uploaded file: {e}")
        raise HTTPException(status_code=400, detail="Failed to read the uploaded file.")

    # Parse content into page-size chunks
    try:
        chunks = await parse_file(content)
        logger.info("Document parsed successfully.")
    except Exception as e:
        logger.error(f"Error parsing the document: {e}")
        raise HTTPException(
            status_code=400, detail=f"Failed to parse the document: {e}"
        )

    # Create embeddings for each chunk
    try:
        embeddings = await create_embeddings(chunks)
        logger.info(
            f"All chunks embedded successfully. Total chunks: {len(embeddings)}"
        )
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        raise HTTPException(status_code=500, detail="Failed to create embeddings.")

    # Convert to DocumentDB schema
    documents = []
    for chunk_id, (text, embedding_vector) in enumerate(zip(chunks, embeddings)):
        document = DocumentDB(
            file_name=file_name,
            chunk_id=chunk_id,
            text=text,
            embedding_vector=embedding_vector,
        )
        documents.append(document)

    # Save documents to the DB
    try:
        await save_document_to_db(documents=documents, asession=asession)
        logger.info("Embeddings stored successfully in the database.")
    except Exception as e:
        logger.error(f"Error saving documents to the database: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to save documents to the database."
        )

    document_ids = [doc.uuid for doc in documents]

    return DocumentResponse(
        status="success",
        message="Document uploaded and embeddings stored.",
        document_ids=document_ids,
    )

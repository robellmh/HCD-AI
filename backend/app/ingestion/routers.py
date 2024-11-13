from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import authenticate_key
from ..database import get_async_session
from ..ingestion.schemas import IngestionResponse
from ..services.DocumentService import DocumentService
from .utils import create_embeddings, parse_file

TAG_METADATA = {
    "name": "Document Ingestion",
    "description": "Endpoints for uploading and processing documents.",
}

router = APIRouter(
    dependencies=[Depends(authenticate_key)],
    tags=["Document Ingestion"],
)


@router.post("/ingestion", response_model=IngestionResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
) -> IngestionResponse:
    """
    Upload and process a document, then store embeddings in the database.
    """
    file_name = file.filename or "unknown filename"
    try:
        content = await file.read()
        chunks = await parse_file(content)
        embeddings = await create_embeddings(chunks)

        file_id = await DocumentService.save_document(
            text_embeddings=list(zip(chunks, embeddings)),
            file_name=file_name,
            session=session,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process document: {e}"
        ) from e

    return IngestionResponse(
        file_name=file_name, file_id=file_id, total_chunks=len(embeddings)
    )

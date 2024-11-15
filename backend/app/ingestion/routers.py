from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import authenticate_key
from ..database import get_async_session
from ..ingestion.schemas import DocumentInfoList, IngestionResponse
from ..services.DocumentService import DocumentService

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
        chunks = await DocumentService.parse_file(content)
        embeddings = await DocumentService.create_embeddings(chunks)

        file_id = await DocumentService.save_document(
            text_embeddings=list(zip(chunks, embeddings)),
            file_name=file_name,
            session=session,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to process document: {e}"
        ) from e

    return IngestionResponse(
        file_name=file_name, file_id=file_id, total_chunks=len(embeddings)
    )


@router.get("/ingestion/list_docs", response_model=DocumentInfoList)
async def get_doc_list(
    session: AsyncSession = Depends(get_async_session),
) -> DocumentInfoList:
    """
    Return a list of all documents in the database.
    """
    return await DocumentService.list_all_docs(session)

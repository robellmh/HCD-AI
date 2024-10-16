from fastapi import APIRouter, Depends

from ..auth.dependencies import authenticate_key
from .schemas import DocumentRequest, DocumentResponse

router = APIRouter(dependencies=[Depends(authenticate_key)], tags=["Document"])


@router.post("/document")
async def upload_document(document_request: DocumentRequest) -> DocumentResponse:
    """
    Handle document uploads.
    """
    return DocumentResponse(status="Document uploaded successfully")

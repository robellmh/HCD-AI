from fastapi import APIRouter, HTTPException

from backend.app.document.schemas import DocumentRequest, DocumentResponse

router = APIRouter()


# POST endpoint for uploading a document
@router.post("/upload", response_model=DocumentResponse)
def upload_document(request: DocumentRequest) -> DocumentResponse:
    """
    Upload a document.

    Args:
        request (DocumentRequest): The document data to be uploaded.

    Returns:
        DocumentResponse: A response containing the upload status and data.
    """
    if not request.title or not request.content:
        raise HTTPException(
            status_code=400, detail="Document title and content are required."
        )

    return DocumentResponse(
        message="Document uploaded successfully", data={"title": request.title}
    )


# GET endpoint for getting a document by ID
@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str) -> DocumentResponse:
    """
    Retrieve a document by ID.

    Args:
        document_id (str): The ID of the document to retrieve.

    Returns:
        DocumentResponse: A response containing the document data.
    """
    document_data = {"title": f"Document {document_id}", "content": "Document content"}

    if not document_data:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        message="Document retrieved successfully", data=document_data
    )

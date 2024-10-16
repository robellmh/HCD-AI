from pydantic import BaseModel


class DocumentRequest(BaseModel):
    """Request schema for document operations"""

    document_id: str
    content: str


class DocumentResponse(BaseModel):
    """Response schema for document operations"""

    status: str
    message: str

from typing import Any, Dict

from pydantic import BaseModel


class DocumentRequest(BaseModel):
    """
    Schema for the document request.

    Attributes:
        title (str): The title of the document.
        content (str): The content of the document.
    """

    title: str
    content: str


class DocumentResponse(BaseModel):
    """
    Schema for the document response.

    Attributes:
        message (str): A message indicating the result of the operation.
        data (Dict[str, Any]): The data related to the document.
    """

    message: str
    data: Dict[str, Any]

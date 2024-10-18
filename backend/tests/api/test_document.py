import pytest
from fastapi.testclient import TestClient

from backend.app.auth.config import API_SECRET_KEY
from backend.app.document.routers import router

# Create a test client using the FastAPI app and mount the router
client = TestClient(router)


@pytest.mark.parametrize(
    "document_data, status_code",
    [
        ({"title": "Test Document", "content": "This is a test."}, 200),
        ({"title": "", "content": "This is a test."}, 400),  # Missing title
        ({"title": "Test Document", "content": ""}, 400),  # Missing content
    ],
)
def test_upload_document(document_data: dict, status_code: int) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.post("/upload", json=document_data, headers=headers)
    assert response.status_code == status_code


def test_get_document() -> None:
    document_id = "1"  # Simulate a document ID to test retrieval
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # First, we should upload a document before retrieving it
    upload_response = client.post(
        "/upload",
        json={"title": "Sample Document", "content": "This is a sample document."},
        headers=headers,
    )

    assert (
        upload_response.status_code == 200
    )  # Ensure the document was uploaded successfully

    # Now, retrieve the document using the ID
    response = client.get(f"/{document_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Document retrieved successfully"
    assert (
        response.json()["data"]["title"] == "Document 1"
    )  # Adjust according to your logic


def test_get_nonexistent_document() -> None:
    document_id = "999"  # ID that doesn't exist
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.get(f"/{document_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

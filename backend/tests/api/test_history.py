from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.auth.config import API_SECRET_KEY
from backend.app.history.routers import (
    router,
)  # Adjust the import based on your project structure

# Create a test client using the FastAPI app and mount the router
client = TestClient(router)


@pytest.mark.parametrize(
    "history_data, expected_status",
    [
        (
            {
                "chat_id": uuid4(),
                "created_by": "Alice",
                "responses": [{"answer": "This is the first response."}],
            },
            200,
        ),
        (
            {
                "chat_id": uuid4(),
                "created_by": "Bob",
                "responses": [],
            },
            200,
        ),
    ],
)
def test_user_history(history_data: dict, status_code: int) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.post("/history", json=history_data, headers=headers)
    assert response.status_code == status_code


def test_get_history_by_chat_id() -> None:
    chat_id = uuid4()  # Create a new UUID for testing
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # First, create a history entry for the chat_id
    create_response = client.post(
        "/history",
        json={
            "chat_id": chat_id,
            "created_by": "Test User",
            "responses": [{"answer": "This is a test response."}],
        },
        headers=headers,
    )

    assert create_response.status_code == 200  # Ensure history was created successfully

    # Now, retrieve the history using the chat_id
    response = client.get(f"/history/{chat_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["history"]["chat_id"] == str(
        chat_id
    )  # Check that the retrieved history matches the created one
    assert (
        response.json()["history"]["created_by"] == "Test User"
    )  # Validate created_by in response
    assert response.json()["history"]["responses"] == [
        {"answer": "This is a test response."}
    ]  # Validate responses


def test_get_history_for_nonexistent_chat_id() -> None:
    nonexistent_chat_id = uuid4()  # Create a UUID that has not been used
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.get(f"/history/{nonexistent_chat_id}", headers=headers)
    assert (
        response.status_code == 404
    )  # Ensure that a 404 status code is returned for non-existent history


def test_get_history_by_created_by() -> None:
    chat_id = uuid4()  # Create a new UUID for testing
    created_by = "Alice"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # Create a history entry
    create_response = client.post(
        "/history",
        json={
            "chat_id": chat_id,
            "created_by": created_by,
            "responses": [{"answer": "This is another test response."}],
        },
        headers=headers,
    )

    assert create_response.status_code == 200  # Ensure history was created successfully

    # Retrieve history entries by created_by
    response = client.get(f"/history/user/{created_by}", headers=headers)
    assert response.status_code == 200
    assert (
        len(response.json()["histories"]) == 1
    )  # Check that we received one history entry
    assert (
        response.json()["histories"][0]["created_by"] == created_by
    )  # Validate created_by in response
    assert response.json()["histories"][0]["responses"] == [
        {"answer": "This is another test response."}
    ]  # Validate responses

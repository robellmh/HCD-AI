from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.auth.config import API_SECRET_KEY
from backend.app.feedback.routers import (
    router,
)  # Adjust the import based on your project structure

# Create a test client using the FastAPI app and mount the router
client = TestClient(router)


@pytest.mark.parametrize(
    "feedback_data, expected_status",
    [
        (
            {
                "user_name": "John Doe",
                "chat_id": uuid4(),
                "feedback_text": "Great chat!",
            },
            200,
        ),
        (
            {"user_name": "", "chat_id": uuid4(), "feedback_text": "No username!"},
            200,
        ),  # Username is empty but feedback can still be submitted
        (
            {"user_name": "Jane Doe", "chat_id": uuid4(), "feedback_text": ""},
            200,
        ),  # Feedback text is empty but feedback can still be submitted
    ],
)
def test_feedback_submission(feedback_data: dict, status_code: int) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.post("/feedback", json=feedback_data, headers=headers)
    assert response.status_code == status_code


def test_get_feedback_by_chat_id() -> None:
    chat_id = uuid4()  # Create a new UUID for testing
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # First, submit feedback for the chat_id
    submit_response = client.post(
        "/feedback",
        json={
            "user_name": "Test User",
            "chat_id": chat_id,
            "feedback_text": "This is a feedback comment.",
        },
        headers=headers,
    )

    assert (
        submit_response.status_code == 200
    )  # Ensure feedback was submitted successfully

    # Now, retrieve feedback using the chat_id
    response = client.get(f"/feedback/{chat_id}", headers=headers)
    assert response.status_code == 200
    assert (
        len(response.json()["feedbacks"]) == 1
    )  # Check that we received one feedback entry
    assert (
        response.json()["feedbacks"][0]["user_name"] == "Test User"
    )  # Validate user name in response
    assert (
        response.json()["feedbacks"][0]["feedback_text"]
        == "This is a feedback comment."
    )  # Validate feedback text


def test_get_feedback_for_nonexistent_chat_id() -> None:
    nonexistent_chat_id = uuid4()  # Create a UUID that has not been used
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.get(f"/feedback/{nonexistent_chat_id}", headers=headers)
    assert response.status_code == 200  # Ensure that the response is successful
    assert response.json()["feedbacks"] == []  # Expect an empty list for no feedback

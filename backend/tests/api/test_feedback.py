from uuid import uuid4

import pytest
from app.auth.config import API_SECRET_KEY
from app.feedback.routers import (
    router,
)  # Adjust the import based on your project structure
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Create a test client using the FastAPI app and mount the router
client = TestClient(router)


@pytest.mark.parametrize(
    "feedback_data, expected_status",
    [
        (
            {
                "user_name": "John Doe",
                "chat_id": str(uuid4()),
                "like": True,
                "feedback_text": "Great chat!",
            },
            200,
        ),
        (
            {
                "user_name": "",
                "chat_id": str(uuid4()),
                "like": False,
                "feedback_text": "No username!",
            },
            200,
        ),  # Username is empty but feedback can still be submitted
        (
            {
                "user_name": "Jane Doe",
                "like": True,
                "chat_id": str(uuid4()),
                "feedback_text": "",
            },
            200,
        ),  # Feedback text is empty but feedback can still be submitted
    ],
)
def test_feedback_submission(feedback_data: dict, expected_status: int) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.post("/feedback", json=feedback_data, headers=headers)
    # Dump the response as JSON to validate structure

    assert (
        response.status_code == expected_status
    )  # Ensure the response contains the "feedback" key

    feedback_response = response.json()
    assert (
        "feedback" in feedback_response
    )  # Ensure the response contains the "feedback" key


def test_get_feedback_by_chat_id() -> None:
    chat_id = str(uuid4())
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    sample_feedback = {
        "user_name": "Test User",
        "chat_id": chat_id,
        "like": True,
        "feedback_text": "This is a test feedback comment.",
    }

    # Submit feedback
    create_response = client.post(
        "/feedback",
        json=sample_feedback,
        headers=headers,
    )

    assert create_response.status_code == 200  # Check feedback submission status

    # Retrieve feedback by chat_id
    response = client.get(f"/feedback/{chat_id}", headers=headers)
    assert response.status_code == 200  # Check retrieval status

    feedback_response = response.json()
    assert feedback_response["feedback"]  # Ensure the feedbacks list is not empty

    # Validate feedback text


def test_get_feedback_for_nonexistent_chat_id() -> None:
    nonexistent_chat_id = uuid4()  # Create a UUID that has not been used
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # Expecting a 404 status code for nonexistent feedback
    with pytest.raises(HTTPException) as err:
        client.get(f"/feedback/user/{nonexistent_chat_id}", headers=headers)
    assert err.value.status_code == 404

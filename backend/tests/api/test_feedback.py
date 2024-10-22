from uuid import uuid4

import pytest
from app.auth.config import API_SECRET_KEY
from app.feedback.routers import (
    router,
)  # Adjust the import based on your project structure
from app.feedback.schemas import FeedbackRequest
from fastapi.testclient import TestClient

# Create a test client using the FastAPI app and mount the router
client = TestClient(router)


@pytest.mark.parametrize(
    "feedback_data, expected_status",
    [
        (
            FeedbackRequest(
                user_name="John Doe",
                chat_id=str(uuid4()),
                like=True,
                feedback_text="Great chat!",
            ),
            200,
        ),
        (
            FeedbackRequest(
                user_name="",
                chat_id=str(uuid4()),
                like=False,
                feedback_text="No username!",
            ),
            200,
        ),  # Username is empty but feedback can still be submitted
        (
            FeedbackRequest(
                user_name="Jane Doe", like=True, chat_id=str(uuid4()), feedback_text=""
            ),
            200,
        ),  # Feedback text is empty but feedback can still be submitted
    ],
)
def test_feedback_submission(
    feedback_data: FeedbackRequest, expected_status: int
) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.post(
        "/feedback", json=feedback_data.model_dump_json(), headers=headers
    )
    assert response.status_code == expected_status


def test_get_feedback_by_chat_id() -> None:
    chat_id = str(uuid4())  # Create a new UUID for testing
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # First, submit feedback for the chat_id using the Pydantic model
    feedback_data = FeedbackRequest(
        user_name="Test User",
        chat_id=chat_id,
        feedback_text="This is a feedback comment.",
    )

    submit_response = client.post(
        "/feedback",
        json=feedback_data.model_dump_json(),
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
    nonexistent_chat_id = str(uuid4())  # Create a UUID that has not been used
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # Make the GET request for the nonexistent chat ID
    response = client.get(f"/feedback/{nonexistent_chat_id}", headers=headers)

    # Expecting a 400 status code for nonexistent feedback
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Feedback not found"
    }  # Check the detail message

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from app.auth.config import API_SECRET_KEY
from app.feedback.routers import router
from app.services.FeedbackService import FeedbackService
from fastapi.testclient import TestClient

client = TestClient(router)


# Test for feedback submission
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
        ),
        (
            {
                "user_name": "Jane Doe",
                "like": True,
                "chat_id": str(uuid4()),
                "feedback_text": "",
            },
            200,
        ),
    ],
)
@patch.object(FeedbackService, "submit_feedback", new_callable=AsyncMock)
async def test_feedback_submission(
    mock_submit_feedback: AsyncMock, feedback_data: dict, expected_status: int
) -> None:
    # Mock the response of the submit_feedback method
    mock_submit_feedback.return_value = (
        feedback_data  # Simulate successful feedback submission
    )

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.post("/feedback", json=feedback_data, headers=headers)

    assert response.status_code == expected_status
    feedback_response = response.json()
    assert "feedback" in feedback_response
    assert isinstance(feedback_response["feedback"], dict)

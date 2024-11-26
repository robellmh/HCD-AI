import os

import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")


def submit_feedback(user_id: str, feedback: str) -> dict:
    """
    Sends feedback from a user to the feedback API.

    Parameters:
        user_id (str): The user's unique ID.
        feedback (str): The feedback content.

    Returns:
        dict: The API's response confirming feedback submission.
    """
    try:
        response = requests.post(
            f"{API_URL}/feedback", json={"user_id": user_id, "feedback": feedback}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

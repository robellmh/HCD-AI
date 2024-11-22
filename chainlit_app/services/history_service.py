import os
from typing import Any

import requests

API_URL: str = os.getenv("API_URL", "http://localhost:8000")


def get_history(user_id: str) -> dict[str, Any]:
    """
    Fetches chat history for a given user ID.

    Args:
        user_id (str): The user's unique ID.

    Returns:
        dict: The API's response containing the history.
    """
    try:
        response: requests.Response = requests.get(
            f"{API_URL}/history", params={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

from typing import Any

import requests  # type: ignore

from ..config import API_URL


def get_history(user_id: str) -> dict[str, Any]:
    """
    Fetches chat history for a given user ID.

    Parameters:
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

import os

import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_SECRET_KEY = os.getenv("SECRET_KEY", "my_secret_key")  # Default if not set in env


def get_chat_response(user_message: str) -> dict:
    """
    Sends the user's message to the chat API and retrieves the response.

    Parameters:
        user_message (str): The message from the user.

    Returns:
        dict: The API's response with 'answer' and 'sources'.
    """
    headers = {"Authorization": f"Bearer {API_SECRET_KEY}"}
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"message": user_message},
            headers=headers,  # Include the authorization header
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

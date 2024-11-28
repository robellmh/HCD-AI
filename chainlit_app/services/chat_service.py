import logging

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "http://backend:8000"
API_SECRET_KEY = "my_secret_key"

logging.basicConfig(level=logging.INFO)

# Set a higher timeout value
TIMEOUT = httpx.Timeout(100.0)  # Adjust as needed


async def get_chat_response(user_id: str, chat_id: str, user_message: str) -> dict:
    """
    Get a response from the chat API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "message": user_message,
    }

    logging.info(f"Sending request to {API_URL}/chat")
    logging.info(f"Headers: {headers}")
    logging.info(f"Payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{API_URL}/chat", headers=headers, json=payload
            )
            response.raise_for_status()  # Raises an exception for 4xx and 5xx responses
            data = response.json()
            return data  # Returns the JSON response as a dictionary
    except httpx.RequestError as exc:
        logging.error(f"An error occurred while requesting {API_URL}/chat: {exc}")
        return {"error": "An error occurred while requesting chat"}
    except httpx.HTTPStatusError as exc:
        logging.error(
            f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}"
        )
        return {"error": f"HTTP error occurred: {exc.response.status_code}"}

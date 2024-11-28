import logging
import os

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "http://backend:8000"
# Unexpected error: Invalid port: 'backend'
API_SECRET_KEY = os.getenv("SECRET_KEY", "my_secret_key")

logging.basicConfig(level=logging.INFO)


async def get_chat_response(user_id: int, chat_id: str, user_message: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    payload = {
        "chat_id": chat_id,
        "user_id": 0,
        "message": user_message,
    }

    logging.info(f"Sending request to {API_URL}/chat")
    logging.info(f"Headers: {headers}")
    logging.info(f"Payload: {payload}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/chat", json=payload, headers=headers
            )
            logging.info(f"Response status: {response.status_code}")
            logging.info(f"Response body: {response.text}")

            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()  # Parse JSON response
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}"}
        except httpx.RequestError as e:
            logging.error(f"Request error: {e}")
            return {"error": "Request failed"}
        except ValueError as e:
            logging.error(f"Response parsing error: {e}")
            return {"error": "Invalid response format"}

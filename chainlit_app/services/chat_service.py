import httpx

from ..config import API_URL

TIMEOUT = httpx.Timeout(100.0)


class ChatServiceError(Exception):
    """Custom exception for chat service errors."""

    # Had to add to satisfy MyPY - httpx errors don't derive from
    # base exception
    pass


async def get_chat_response(
    user_id: str, chat_id: str, user_message: str, token: str
) -> dict:
    """
    Sends an asynchronous POST request to the chat API to retrieve a chat response.

    Parameters:
    - user_id (str): The unique identifier for the user requesting the chat.
    - chat_id (str): The unique identifier for the chat session.
    - user_message (str): The message from the user to be sent to the chat API.
    - token (str): The token for authorizing the request against the API.

    Returns:
    - dict: A dictionary containing the API's response data.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "chat_id": chat_id,
        "user_id": user_id,
        "message": user_message,
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{API_URL}/chat", headers=headers, json=payload
            )
            response.raise_for_status()
            return response.json()

    except httpx.RequestError as exc:
        raise ChatServiceError(
            f"An error occurred while requesting chat: {exc}"
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise ChatServiceError(
            f"HTTP error occurred: {exc.response.status_code} \n{exc.response.text}"
        ) from exc

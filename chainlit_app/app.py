import uuid

import chainlit as cl
import httpx

from chainlit_app.config import API_URL
from chainlit_app.services.chat_service import get_chat_response


@cl.password_auth_callback
async def auth_callback(username: str, password: str) -> cl.User | None:
    """
    Authenticate by using a FastAPI endpoint that returns a JWT token.
    Returns a user object with the JWT token if authentication is successful.
    Otherwise, returns None.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Use form-encoded data
            response = await client.post(
                f"{API_URL}/login",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                },
            )

        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return cl.User(
                    identifier=username,
                    metadata={
                        "role": "user",
                        "provider": "jwt",
                        "token": data["access_token"],
                    },
                )
        else:
            await cl.Message(
                content=f"Authentication failed with status code:\
                {response.status_code}"
            ).send()
            return None

    except httpx.HTTPStatusError as exc:
        await cl.Message(
            content=f"HTTP error occurred: {exc.response.status_code}"
        ).send()
    except Exception as e:
        await cl.Message(
            content=f"An error occurred during authentication: {str(e)}"
        ).send()
        return None
    return None


@cl.on_chat_start
async def chat_start() -> None:
    """
    Triggered when the chat starts. Initializes a unique chat session ID.
    """
    # Generate a UUID for all new chat sessions
    session_id = str(uuid.uuid4())
    cl.user_session.set("chat_session_id", session_id)

    app_user = cl.user_session.get("user")
    await cl.Message(
        content=f"Hello, {app_user.identifier}! How can I assist you today?"
    ).send()


@cl.on_message
async def main(message: cl.Message) -> None:
    """
    Handles user messages and provides a response from the chat API using a JWT token.
    """
    user_message = message.content

    # Retrieve the user session to get the JWT token
    app_user = cl.user_session.get("user")
    token = app_user.metadata.get("token") if app_user and app_user.metadata else None

    if not token:
        await cl.Message(
            content="Authentication error: Unable to retrieve JWT token. \
                Please log in again."
        ).send()
        return

    # Retrieve the session ID
    chat_session_id = cl.user_session.get("chat_session_id")
    if not chat_session_id:
        await cl.Message(
            content="Error: No chat session ID found. Please start a new session."
        ).send()
        return

    await cl.Message(content="Processing your request...").send()

    # Pass the token and chat session ID to the chat service
    response = await get_chat_response(
        chat_session_id=chat_session_id, user_message=user_message, token=token
    )

    if "response" in response:
        await cl.Message(content=response["response"]).send()
    elif "error" in response:
        await cl.Message(content=response["error"]).send()
    else:
        await cl.Message(content="An unexpected error occurred.").send()

import chainlit as cl
from services.chat_service import get_chat_response


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> None:
    """

     Fetch the user matching username from your database
    and compare the hashed password with the value stored in the database
    """
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_chat_start
async def chat_start() -> None:
    """

    Triggered when the chat starts. Welcomes the user
    and gives options to fetch history.
    """
    app_user = cl.user_session.get("user")
    await cl.Message(
        content=f"Hello, {app_user.identifier}! How can I assist today?"
    ).send()


@cl.on_message
async def main(message: cl.Message) -> None:
    """
    Handles user messages and provides a response from the chat API.
    """
    user_message = message.content
    chat_id = ""
    user_id = 0

    await cl.Message(content="Processing your request...").send()

    response = await get_chat_response(user_id, chat_id, user_message)

    if "response" in response:
        await cl.Message(content=response["response"]).send()
    elif "error" in response:
        await cl.Message(content=response["error"]).send()
    else:
        await cl.Message(content="An unexpected error occurred.").send()

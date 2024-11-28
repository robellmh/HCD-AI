import chainlit as cl
from services.chat_service import get_chat_response


@cl.on_chat_start
async def chat_start() -> None:
    """
    Triggered when the chat starts. Welcomes the user.
    """
    await cl.Message(
        content="Welcome! You can ask questions on health services delivery."
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

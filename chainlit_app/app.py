import chainlit as cl
import services.chat_service
import services.feedback_service
import services.history_service


@cl.on_chat_start
async def chat_start() -> None:
    """
    Triggered when the chat starts. Welcomes the user
    and gives options to fetch history.
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

    response = services.chat_service.get_chat_response(user_message)
    if "error" in response:
        await cl.Message(content=f"Error: {response['error']}").send()
    else:
        answer = response.get("answer", "No answer found.")
        sources = response.get("sources", [])
        source_info = (
            f"Sources: {', '.join(sources)}" if sources else "No sources found."
        )
        await cl.Message(content=f"{answer}\n{source_info}").send()

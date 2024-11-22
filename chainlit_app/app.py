import services.chat_service
import services.feedback_service
import services.history_service
from chainlit import Message, on_chat_start, on_message


@on_chat_start
async def chat_start() -> None:
    """
    Triggered when the chat starts. Welcomes the user
    and gives options to fetch history.
    """
    await Message(
        content="Welcome! You can ask questions on health services delivery."
    ).send()


@on_message
async def main(message: Message) -> None:
    """
    Handles user messages and provides a response from the chat API.
    """
    user_message = message.content

    response = services.chat_service.get_chat_response(user_message)
    if "error" in response:
        await Message(content=f"Error: {response['error']}").send()
    else:
        answer = response.get("answer", "No answer found.")
        sources = response.get("sources", [])
        source_info = (
            f"Sources: {', '.join(sources)}" if sources else "No sources found."
        )
        await Message(content=f"{answer}\n{source_info}").send()


# @cl.on_message
# async def fetch_history(message: cl.Message):
#     """
#     Handles fetching user chat history based on user ID.
#     """
#     user_id = message.content  # Assume the user provides their ID
#     history = services.history_service.get_history(user_id)

#     if "error" in history:
#         await cl.Message(content=f"Error: {history['error']}").send()
#     else:
#         await cl.Message(
#             content=f"Your Chat History: {history.get('history', [])}"
#         ).send()


# @cl.on_message
# async def provide_feedback(message: cl.Message):
#     """
#     Handles user feedback submission.
#     """
#     feedback = message.content  # Assume the user provides their feedback
#     response = services.feedback_service.submit_feedback(
#         user_id="123", feedback=feedback
#     )  # Example user_id

#     if "error" in response:
#         await cl.Message(content=f"Error: {response['error']}").send()
#     else:
#         await cl.Message(content="Thank you for your feedback!").send()

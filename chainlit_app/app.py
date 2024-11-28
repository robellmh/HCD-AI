import asyncio

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
    chat_id = ""
    # user_session = cl.UserSession.get()

    # if user_session and user_session.user_id:
    #     user_id = user_session.user_id
    #     # Attach custom data to the session
    #     user_session.set("custom_data", {"user_name": "John Doe"})
    # else:
    user_id = ""
    await cl.Message(content="Processing your request...").send()

    try:
        response = await asyncio.wait_for(
            services.chat_service.get_chat_response(user_id, chat_id, user_message),
            timeout=100,
        )

        if "error" in response:
            await cl.Message(content=f"Error: {response['error']}").send()
        else:
            answer = response.get("answer", "No answer found.")
            sources = response.get("sources", [])
            source_info = (
                f"Sources: {', '.join(sources)}" if sources else "No sources found."
            )
            await cl.Message(content=f"{answer}\n{source_info}").send()
    except asyncio.TimeoutError:
        await cl.Message(content="The service took too long to respond.").send()
    except Exception as e:
        await cl.Message(content=f"Unexpected error: {e}").send()

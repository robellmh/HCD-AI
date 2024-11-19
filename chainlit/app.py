import requests

import chainlit as cl  # Ensure the correct module and attributes are imported

API_URL = "http://localhost:8000"  # Adjust the URL as needed


# Add type annotations for all functions
@cl.on_chat_start
async def on_chat_start() -> None:
    """
    Triggered when the chat starts. It waits for the user to upload PDF files
    and uploads them to the API.

    Args:
        None

    Returns:
        None
    """
    files = None  # Initialize variable to store uploaded files

    # Wait for the user to upload files
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload one or more PDF files to begin!",
            accept=["application/pdf"],
            max_size_mb=500,  # Optionally limit the file size
            max_files=10,
            timeout=180,  # Set a timeout for user response
        ).send()

    # Upload files to the API
    try:
        # Prepare files for upload
        files_to_send = [
            ("files", (file.name, file.file, file.content_type)) for file in files
        ]

        upload_response = requests.post(f"{API_URL}/upload", files=files_to_send)
        upload_response.raise_for_status()  # Raises an exception for 4xx/5xx responses

        # Inform the user of successful upload
        await cl.Message(
            content="Files uploaded successfully! You can now ask questions."
        ).send()

    except requests.RequestException as e:
        # Send error message to user if upload fails
        await cl.Message(content=f"Error uploading files: {str(e)}").send()


# Add type annotations for 'main' function and ensure 'message'
#  parameter is of type 'cl.Message'
@cl.on_message
async def main(message: cl.Message) -> None:
    """
    Handles incoming user messages. Sends the message to an API and
    returns the answer with any related sources.

    Args:
        message (cl.Message): The incoming message object containing user content.

    Returns:
        None
    """
    user_message = message.content

    try:
        # Call the chat API
        response = requests.post(f"{API_URL}/chat", json={"message": user_message})
        response.raise_for_status()  # Raises an exception for 4xx/5xx responses

        # Get the answer and sources from the API response
        api_response = response.json()
        answer = api_response.get("answer", "No answer found.")
        sources = api_response.get("sources", [])

        source_info = (
            f"Sources: {', '.join(sources)}" if sources else "No sources found."
        )
        await cl.Message(content=f"{answer}\n{source_info}").send()

    except requests.RequestException as e:
        # Handle API request errors
        await cl.Message(content=f"Error: {str(e)}").send()

from unittest.mock import AsyncMock, patch

import pytest

from chainlit.app import main, on_chat_start


@pytest.mark.asyncio
async def test_on_chat_start():
    # Create a mock for cl.AskFileMessage
    with patch("chainlit.AskFileMessage.send", new_callable=AsyncMock) as mock_send:
        # Call the function
        await on_chat_start()
        # Assert that send was called
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_main():
    # Create a mock message
    mock_message = AsyncMock()
    mock_message.content = "Test message"
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "answer": "Test answer",
            "sources": [],
        }
        await main(mock_message)
        # Assert that post was called correctly
        mock_post.assert_called_once_with(
            "http://localhost:8000/chat", json={"message": "Test message"}
        )

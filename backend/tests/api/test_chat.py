from uuid import uuid4

from app.auth.config import API_SECRET_KEY
from fastapi.testclient import TestClient


# Test for starting a new chat
def test_start_chat(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # Dump the Pydantic model as JSON
    response = client.post(
        "/chat",
        headers=headers,
        json={"user_name": "Test User", "created_date_time": "2024-10-16T12:00:00Z"},
    )

    assert response.status_code == 200
    assert "Chat started successfully with ID:" in response.json()["response"]


# Test for retrieving a chat by ID
def test_get_chat(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    start_response = client.post(
        "/chat",
        headers=headers,
        json={"user_name": "Test User", "created_date_time": "2024-10-16T12:00:00Z"},
    )
    chat_id = start_response.json()["response"].split(": ")[-1]  # Extract the chat ID

    response = client.get(f"/chat/{chat_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["chat"]["user_name"] == "Test User"


# Test for asking a question in a chat
def test_ask_question(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    start_response = client.post(
        "/chat",
        headers=headers,
        json={"user_name": "Test User2", "created_date_time": "2024-10-16T12:00:00Z"},
    )
    chat_id = start_response.json()["response"].split(": ")[-1]  # Extract the chat ID

    # Dump the Pydantic model as JSON
    response = client.post(
        f"/chat/{chat_id}/ask",
        headers=headers,
        json={"question": "What is the capital of Ethiopia?"},
    )

    assert response.status_code == 200
    assert "Answer to your question" in response.json()["answer"]


# Test for getting a non-existent chat
def test_get_non_existent_chat(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    non_existent_chat_id = str(uuid4())  # Generate a random UUID that won't exist
    response = client.get(f"/chat/{non_existent_chat_id}", headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}

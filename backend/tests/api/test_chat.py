from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.auth.config import API_SECRET_KEY


@pytest.fixture
def client() -> TestClient:
    from backend.app.main import (
        app,
    )  # Adjust this import according to your project structure

    return TestClient(app)


# Test for starting a new chat
def test_start_chat(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # Sample data for the new chat request
    new_chat_data = {
        "user_name": "Test User",
        "created_date_time": "2024-10-16T12:00:00Z",  # Example ISO format datetime
    }

    response = client.post("/chat", headers=headers, json=new_chat_data)

    assert response.status_code == 200
    assert "Chat started successfully with ID:" in response.json()["response"]


# Test for retrieving a chat by ID
def test_get_chat(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    # Start a chat first to get a valid chat_id
    new_chat_data = {
        "user_name": "Test User",
        "created_date_time": "2024-10-16T12:00:00Z",
    }
    start_response = client.post("/chat", headers=headers, json=new_chat_data)
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

    # Start a chat first to get a valid chat_id
    new_chat_data = {
        "user_name": "Test User",
        "created_date_time": "2024-10-16T12:00:00Z",
    }
    start_response = client.post("/chat", headers=headers, json=new_chat_data)
    chat_id = start_response.json()["response"].split(": ")[-1]  # Extract the chat ID

    # Sample data for the ask question request
    ask_question_data = {
        "question": "What is the capital of Ethiopia?",
    }

    response = client.post(
        f"/chat/{chat_id}/ask", headers=headers, json=ask_question_data
    )

    assert response.status_code == 200
    assert "Answer to your question" in response.json()["answer"]


# Test for getting a non-existent chat
def test_get_non_existent_chat(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    non_existent_chat_id = uuid4()  # Generate a random UUID that won't exist
    response = client.get(f"/chat/{non_existent_chat_id}", headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}

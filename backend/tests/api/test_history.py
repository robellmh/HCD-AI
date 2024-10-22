from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.auth.config import API_SECRET_KEY
from backend.app.history.routers import router

client = TestClient(router)


@pytest.mark.parametrize(
    "history_data, expected_status",
    [
        (
            {
                "chat_id": uuid4(),
                "created_by": "Alice",
                "responses": [{"answer": "This is the first response."}],
            },
            200,
        ),
        (
            {
                "chat_id": uuid4(),
                "created_by": "Bob",
                "responses": [],
            },
            200,
        ),
    ],
)
def test_user_history(history_data: dict, expected_status: int) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.post("/history", json=history_data, headers=headers)
    assert (
        response.status_code == expected_status
    )  # Ensure the status code matches the expected one

    # Dump the response as JSON to validate structure
    history_response = response.json()
    assert (
        "history" in history_response
    )  # Ensure the response contains the "history" key
    assert history_response["history"]["chat_id"] == str(
        history_data["chat_id"]
    )  # Check chat_id
    assert (
        history_response["history"]["created_by"] == history_data["created_by"]
    )  # Check created_by
    assert (
        history_response["history"]["responses"] == history_data["responses"]
    )  # Check responses


def test_get_history_by_chat_id() -> None:
    chat_id = uuid4()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    create_response = client.post(
        "/history",
        json={
            "chat_id": chat_id,
            "created_by": "Test User",
            "responses": [{"answer": "This is a test response."}],
        },
        headers=headers,
    )

    assert create_response.status_code == 200

    response = client.get(f"/history/{chat_id}", headers=headers)
    assert response.status_code == 200

    history_response = response.json()
    assert history_response["history"]["chat_id"] == str(chat_id)
    assert history_response["history"]["created_by"] == "Test User"
    assert history_response["history"]["responses"] == [
        {"answer": "This is a test response."}
    ]


def test_get_history_for_nonexistent_chat_id() -> None:
    nonexistent_chat_id = uuid4()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.get(f"/history/{nonexistent_chat_id}", headers=headers)
    assert response.status_code == 404


def test_get_history_for_nonexistent_user() -> None:
    nonexistent_user = "Nonexistent User"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }
    response = client.get(f"/history/user/{nonexistent_user}", headers=headers)
    assert response.status_code == 404


def test_get_history_by_created_by() -> None:
    chat_id = uuid4()
    created_by = "Alice"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    create_response = client.post(
        "/history",
        json={
            "chat_id": chat_id,
            "created_by": created_by,
            "responses": [{"answer": "This is another test response."}],
        },
        headers=headers,
    )

    assert create_response.status_code == 200

    response = client.get(f"/history/user/{created_by}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["histories"]) == 1
    assert response.json()["histories"][0]["created_by"] == created_by
    assert response.json()["histories"][0]["responses"] == [
        {"answer": "This is another test response."}
    ]

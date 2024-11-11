from typing import AsyncGenerator

import pytest
from app.auth.config import API_SECRET_KEY
from app.chat.models import (
    ChatRequestDB,
    ChatResponseDB,
    save_chat_request,
    save_chat_response,
)
from app.chat.schemas import ChatResponseBase, ChatUserMessageBase
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def chat_message() -> ChatUserMessageBase:
    return ChatUserMessageBase(
        session_id="test_session1", user_id=1, message="test message"
    )


@pytest.fixture
def chat_response() -> ChatResponseBase:
    return ChatResponseBase(
        response="test response",
    )


@pytest.fixture
def headers() -> dict:
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }


async def clean_up_chat_history(asession: AsyncSession) -> None:
    stmt_child = delete(ChatResponseDB)
    await asession.execute(stmt_child)
    stmt_parent = delete(ChatRequestDB)
    await asession.execute(stmt_parent)

    await asession.commit()


@pytest.fixture
async def chat_history(
    headers: dict,
    client: TestClient,
    chat_message: ChatUserMessageBase,
    asession: AsyncSession,
) -> AsyncGenerator[None, None]:
    # Start clean

    await clean_up_chat_history(asession)

    for _ in range(5):
        saved_chat = await save_chat_request(chat_message, asession)
        chat_response = ChatResponseBase(
            response="test response 1", request_id=saved_chat.request_id
        )
        await save_chat_response(chat_response, asession)

    for _ in range(3):
        chat_message.session_id = "test_session2"
        saved_chat = await save_chat_request(chat_message, asession)
        chat_response = ChatResponseBase(
            response="test response 2", request_id=saved_chat.request_id
        )
        await save_chat_response(chat_response, asession)

    yield

    # Delete all chat chat_history
    await clean_up_chat_history(asession)


class TestSingleTurnChat:
    def test_chat_incorrect_token(
        self,
        client: TestClient,
        chat_message: ChatUserMessageBase,
        load_pdf: None,
        headers: dict,
    ) -> None:
        headers["Authorization"] = "Bearer FakeToken"
        response = client.post(
            "/chat",
            headers=headers,
            json=chat_message.model_dump(),
        )

        assert response.status_code == 401

    def test_chat_correct_token(
        self,
        client: TestClient,
        chat_message: ChatUserMessageBase,
        load_pdf: None,
        headers: dict,
    ) -> None:
        response = client.post(
            "/chat",
            headers=headers,
            json=chat_message.model_dump(),
        )

        assert response.status_code == 200

    def test_session_id_not_provided(
        self,
        client: TestClient,
        chat_message: ChatUserMessageBase,
        load_pdf: None,
        headers: dict,
    ) -> None:
        message = chat_message.model_dump()
        message.pop("session_id")
        response = client.post(
            "/chat",
            headers=headers,
            json=message,
        )

        assert response.status_code == 200


class TestRetrieveChat:
    def test_retrieve_nonexistent_session_id(
        self,
        client: TestClient,
        headers: dict,
    ) -> None:
        response = client.get("/chat/123", headers=headers)

        assert response.status_code == 404

    def test_retrieve_correct_session_id(
        self,
        client: TestClient,
        chat_message: ChatUserMessageBase,
        load_pdf: None,
        chat_history: None,
        headers: dict,
    ) -> None:
        response = client.get("/chat/test_session1", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 10

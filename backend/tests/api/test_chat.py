from typing import AsyncGenerator

import pytest
from app.auth.config import API_SECRET_KEY
from app.chat.models import (
    ChatRequestDB,
    ChatResponseDB,
    save_chat_request,
    save_chat_response,
)
from app.chat.routers import update_request_using_history
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


class TestMultiturnChat:
    @pytest.mark.parametrize(
        "session_id, history_exists",
        [("test_session1", True), ("test_session2", True), ("test_session3", False)],
    )
    async def test_chat_history_summary(
        self,
        chat_message: ChatUserMessageBase,
        chat_history: None,
        session_id: str,
        history_exists: bool,
        asession: AsyncSession,
    ) -> None:
        chat_message.session_id = session_id
        original_message = chat_message.message
        new_message = await update_request_using_history(
            chat_request=chat_message, asession=asession
        )

        if history_exists:
            assert new_message.message_original == original_message
            assert new_message.message == "fake_refined_message"
            assert new_message.session_summary == "fake_summary"
        else:
            assert new_message.message_original is None
            assert new_message.message == original_message
            assert new_message.session_summary is None

from pathlib import Path
from typing import AsyncGenerator, Generator

import app
import numpy as np
import pytest
from app import create_app
from app.auth.config import API_SECRET_KEY
from app.config import PGVECTOR_VECTOR_SIZE
from app.database import get_connection_url
from app.ingestion.schemas import DocumentChunk
from app.services.utils.prompts import RAG
from fastapi.testclient import TestClient
from numpy import ndarray
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine


# We recreate engine and session to ensure it is in the same
# event loop as the test. Without this we get "Future attached to different loop" error.
# See https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#using-multiple-asyncio-event-loops
@pytest.fixture(scope="function")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    connection_string = get_connection_url()
    engine = create_async_engine(connection_string, pool_size=20)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def asession(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine, expire_on_commit=False) as async_session:
        yield async_session


@pytest.fixture(scope="session")
def client(patch_llm_call: pytest.FixtureRequest) -> Generator[TestClient, None, None]:
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def load_pdf(client: TestClient) -> None:
    filename = "Ethiopia_DH_CaseStudy.pdf"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    with open(Path(__file__).parent / "data" / filename, "rb") as f:
        files = {"file": (filename, f, "text/plain")}
        response = client.post("/ingestion", headers=headers, files=files)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to load PDF: {response.json()}")


@pytest.fixture(scope="session")
def monkeysession(
    request: pytest.FixtureRequest,
) -> Generator[pytest.MonkeyPatch, None, None]:
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def patch_llm_call(monkeysession: pytest.MonkeyPatch) -> None:
    """Patch the call to the LLM model to return random embeddings"""

    monkeysession.setattr(
        "backend.app.services.DocumentService.DocumentService.create_embeddings",
        async_fake_embedding,
    )
    monkeysession.setattr(app.chat.routers, "get_llm_response", async_fake_llm_response)
    monkeysession.setattr(
        app.services.ChatService, "get_session_summary", async_get_session_summary
    )
    monkeysession.setattr(
        app.services.ChatService,
        "get_refined_message",
        async_get_refined_message,
    )
    monkeysession.setattr(
        app.chat.routers.DocumentService, "rerank_chunks", async_fake_rerank_chunks
    )


async def async_fake_rerank_chunks(
    similar_chunks: dict[int, DocumentChunk], *args: list, **kwargs: dict
) -> dict[int, DocumentChunk]:
    """Fake reranking function that returns the same chunks in a different order."""

    random_order = sorted(similar_chunks.keys(), key=lambda x: np.random.rand())
    return {i: similar_chunks[i] for i in random_order}


async def async_fake_embedding(chunks: list[str]) -> ndarray:
    """Fake embedding function that returns random embeddings."""

    return np.random.rand(len(chunks), int(PGVECTOR_VECTOR_SIZE))


async def async_fake_llm_response(*args: list, **kwargs: dict) -> RAG:
    """Fake LLM response that returns random embeddings."""
    return RAG(
        extracted_info=["fake_info1", "fake_info2"],
        answer="fake_answer",
    )


async def async_get_session_summary(*args: list, **kwargs: dict) -> str:
    return "fake_summary"


async def async_get_refined_message(*args: list, **kwargs: dict) -> str:
    return "fake_refined_message"

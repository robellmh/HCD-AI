from typing import AsyncGenerator, Generator

import numpy as np
import pytest
from app import create_app
from app.config import PGVECTOR_VECTOR_SIZE
from app.database import get_connection_url
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


@pytest.fixture(scope="session")
def monkeysession(
    request: pytest.FixtureRequest,
) -> Generator[pytest.MonkeyPatch, None, None]:
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def patch_llm_call(monkeysession: pytest.MonkeyPatch) -> None:
    """Patch the call to the LLM model to return random embeddings"""

    monkeysession.setattr(
        "backend.app.ingestion.routers.create_embeddings", async_fake_embedding
    )


async def async_fake_embedding(chunks: list[str]) -> ndarray:
    """Fake embedding function that returns random embeddings."""

    return np.random.rand(len(chunks), int(PGVECTOR_VECTOR_SIZE))

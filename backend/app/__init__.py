from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis

from .config import REDIS_HOST
from .utils import setup_logger

from . import (
    document_handling,
)

logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan events for the FastAPI application.
    """

    logger.info("Application started")
    app.state.redis = await aioredis.from_url(REDIS_HOST)

    yield

    await app.state.redis.close()
    logger.info("Application finished")


def create_app() -> FastAPI:
    """
    Create a FastAPI application with the experiments router.
    """
    app = FastAPI(title="HEW-AI Backend API", lifespan=lifespan)

    app.include_router(document_handling.router)

    origins = [
        "http://localhost",
        "http://localhost:3000",
        "https://localhost",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

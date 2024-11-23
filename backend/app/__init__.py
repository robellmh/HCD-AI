from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import CrossEncoder

from .auth import router as auth_router
from .chat import router as chat_router
from .config import CROSS_ENCODER_MODEL, USE_CROSS_ENCODER
from .feedback import router as feedback_router
from .history import router as history_router
from .ingestion import router as ingestion_router
from .search import router as search_router
from .users import router as users_router
from .utils import setup_logger

logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan events for the FastAPI application.
    """

    logger.info("Application started")

    if USE_CROSS_ENCODER == "True":
        app.state.crossencoder = CrossEncoder(
            CROSS_ENCODER_MODEL,
        )

    yield

    logger.info("Application finished")


def create_app() -> FastAPI:
    """
    Create a FastAPI application with the experiments router.
    """
    app = FastAPI(title="HEW-AI Backend API", debug=True)

    app.include_router(ingestion_router)
    app.include_router(search_router)
    app.include_router(chat_router)
    app.include_router(history_router)
    app.include_router(feedback_router)
    app.include_router(users_router)
    app.include_router(auth_router)

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

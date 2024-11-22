from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .chat import router as chat_router
from .feedback import router as feedback_router
from .history import router as history_router
from .ingestion import router as ingestion_router
from .search import router as search_router
from .utils import setup_logger

logger = setup_logger()


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

import logging

import uvicorn
from app import create_app
from app.config import BACKEND_ROOT_PATH
from fastapi.logger import logger

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    # Pass root_path directly to uvicorn.run
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        root_path=BACKEND_ROOT_PATH,
    )

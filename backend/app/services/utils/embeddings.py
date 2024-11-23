from numpy import ndarray
from sentence_transformers import SentenceTransformer

from ...config import EMBEDDING_MODEL_NAME
from ...utils import setup_logger

logger = setup_logger()


async def create_embeddings(chunks: list[str] | str) -> ndarray:
    """
    Create embeddings for a list of text chunks using `sentence_transformers`

    Parameters
    ----------
    chunks
        A list of text chunks.

    Returns
    -------
    ndarray
        A list of embedding vectors corresponding to each text chunk.
    """

    embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME, trust_remote_code=True)

    logger.info(
        f"""Generating embeddings for {len(chunks)} chunks using
                    async batch processing"""
    )
    embeddings = embed_model.encode(chunks)
    logger.info("Embeddings generated successfully")

    return embeddings

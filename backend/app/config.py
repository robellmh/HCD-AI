import os

POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
DB_POOL_SIZE = os.environ.get("DB_POOL_SIZE", 20)  # Number of connections in the pool

BACKEND_ROOT_PATH = os.environ.get("BACKEND_ROOT_PATH", "")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")

# PGVector
PGVECTOR_VECTOR_SIZE = os.environ.get("PGVECTOR_VECTOR_SIZE", 768)  # gte-large-en-v1.5
PGVECTOR_M = os.environ.get("PGVECTOR_M", "16")
PGVECTOR_EF_CONSTRUCTION = os.environ.get("PGVECTOR_EF_CONSTRUCTION", "64")
PGVECTOR_DISTANCE = os.environ.get("PGVECTOR_DISTANCE", "vector_cosine_ops")

# Embeddings
EMBEDDING_MODEL_NAME = os.environ.get(
    "EMBEDDING_MODEL_NAME", "Alibaba-NLP/gte-base-en-v1.5"
)  # Update `PGVECTOR_VECTOR_SIZE` accordingly

LLM_MODEL = os.environ.get("LLM_MODEL", "ollama/llama3.2:1b")  # or "gpt-4o-mini"
LLM_API_BASE = os.environ.get("LLM_API_BASE", "http://localhost:11434")

# Cross-encoder
USE_CROSS_ENCODER = os.environ.get("USE_CROSS_ENCODER", "True")
CROSS_ENCODER_MODEL = os.environ.get(
    "CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

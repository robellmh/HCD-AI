"""Create document tables

Revision ID: 8e185a868bcc
Revises:
Create Date: 2024-10-10 17:32:47.987166

"""

from typing import Sequence, Union

import pgvector
import sqlalchemy as sa
from alembic import op
from app.config import (
    PGVECTOR_DISTANCE,
    PGVECTOR_EF_CONSTRUCTION,
    PGVECTOR_M,
    PGVECTOR_VECTOR_SIZE,
)

# revision identifiers, used by Alembic.
revision: str = "8e185a868bcc"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Add extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.create_table(
        "documents",
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=150), nullable=False),
        sa.Column("file_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "embedding_vector",
            pgvector.sqlalchemy.Vector(dim=int(PGVECTOR_VECTOR_SIZE)),
            nullable=False,
        ),
        sa.Column("created_datetime_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_datetime_utc", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("content_id"),
    )

    op.execute(
        f"""CREATE INDEX documents_embedding_idx ON documents
        USING hnsw (embedding_vector {PGVECTOR_DISTANCE})
        WITH (m = {PGVECTOR_M}, ef_construction = {PGVECTOR_EF_CONSTRUCTION})"""
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "documents_embedding_idx",
        table_name="documents",
        postgresql_using="hnsw",
        postgresql_with={
            "M": {PGVECTOR_M},
            "ef_construction": PGVECTOR_EF_CONSTRUCTION,
        },
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.drop_table("documents")
    op.execute("DROP EXTENSION IF EXISTS vector;")
    # ### end Alembic commands ###

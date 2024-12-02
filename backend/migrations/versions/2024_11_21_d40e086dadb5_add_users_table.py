"""Add users table

Revision ID: d40e086dadb5
Revises: 970ae3c2a1b4
Create Date: 2024-11-21 13:07:40.776402

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d40e086dadb5"
down_revision: Union[str, None] = "970ae3c2a1b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Define the ENUM type for the role column
    role_enum = postgresql.ENUM("admin", "user", name="role_enum")

    # Create the users table
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("role", role_enum, nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_user_id"), "users", ["user_id"], unique=True)


def downgrade() -> None:
    # Drop the users table
    op.drop_index(op.f("ix_users_user_id"), table_name="users")
    op.drop_table("users")

    # Drop the ENUM type for the role column
    role_enum = postgresql.ENUM("admin", "user", name="role_enum")
    role_enum.drop(op.get_bind(), checkfirst=True)

"""added chat tables

Revision ID: 0ac7e03fe00d
Revises: 8e185a868bcc
Create Date: 2024-11-07 22:32:42.627009

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0ac7e03fe00d"
down_revision: Union[str, None] = "5c56714fdbad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "chat_requests",
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.String(), nullable=False),
        sa.Column("created_datetime_utc", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("request_id"),
    )
    op.create_table(
        "chat_responses",
        sa.Column("response_id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("created_datetime_utc", sa.DateTime(), nullable=False),
        sa.Column("response", sa.String(), nullable=False),
        sa.Column("response_metadata", sa.JSON(), nullable=True),
        sa.Column("chat_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["chat_requests.request_id"],
        ),
        sa.PrimaryKeyConstraint("response_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("chat_responses")
    op.drop_table("chat_requests")
    # ### end Alembic commands ###

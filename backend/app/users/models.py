from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base


class UsersDB(Base):
    """ORM for managing user information."""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    role: Mapped[str] = mapped_column(String, nullable=False, default="user")
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

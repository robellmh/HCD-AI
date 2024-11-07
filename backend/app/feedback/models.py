# feedback/models.py

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base


class FeedbackModel(Base):
    """
    SQLAlchemy model representing feedback entries in the database.

    Attributes:
    ----------
    feedback_id : UUID
        Primary key for the feedback entry.
    user_name : str
        The username of the person submitting the feedback.
    chat_id : UUID
        The unique identifier of the chat session associated with the feedback.
    feedback_text : str
        Text content of the feedback.
    like : bool
        Boolean indicating if the feedback is a positive 'like'.
    created_datetime : datetime
        The timestamp when the feedback was created, in UTC.
    """

    __tablename__ = "feedback"

    feedback_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    feedback_text: Mapped[str] = mapped_column(String, nullable=False)
    like: Mapped[bool] = mapped_column(Boolean, default=False)
    created_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..feedback.models import FeedbackModel
from ..feedback.schemas import Feedback, FeedbackRequest


class FeedbackService:
    """
    Service class for handling operations related to user feedback.

    This class provides static methods to submit feedback,
    retrieve feedback by chat ID,
    and retrieve feedback by username. It uses SQLAlchemy for async
    database interactions.
    """

    @staticmethod
    async def submit_feedback(
        feedback_request: FeedbackRequest, session: AsyncSession
    ) -> Feedback:
        """
        Submits feedback to the database.

        Parameters
        ----------
        feedback_request : FeedbackRequest
            The feedback data provided by the user.
        session : AsyncSession
            The async database session.

        Returns
        -------
        Feedback
            The saved feedback entry as a Pydantic model.
        """
        feedback_model = FeedbackModel(
            user_name=feedback_request.user_name,
            chat_id=feedback_request.chat_id,
            feedback_text=feedback_request.feedback_text,
            like=feedback_request.like,
        )
        session.add(feedback_model)
        await session.commit()
        await session.refresh(
            feedback_model
        )  # Refresh to get the updated object from the database

        # Convert the ORM model to a Pydantic model for response
        return Feedback.from_orm(feedback_model)

    @staticmethod
    async def retrieve_feedback_by_chat_id(
        chat_id: UUID, session: AsyncSession
    ) -> Optional[Feedback]:
        """
        Retrieves a feedback entry by chat_id.

        Parameters
        ----------
        chat_id : UUID
            The chat_id for which feedback is retrieved.
        session : AsyncSession
            The async database session.

        Returns
        -------
        Optional[Feedback]
            The feedback entry if found, else None.
        """
        try:
            query = select(FeedbackModel).where(FeedbackModel.chat_id == chat_id)
            result = await session.execute(query)
            feedback = result.scalars().first()
            if feedback is None:
                raise ValueError("Feedback not found")

            return Feedback.from_orm(feedback)
        except Exception as e:
            raise e  # Ensure HTTPException is properly propagated

    @staticmethod
    async def retrieve_feedback_by_user_name(
        user_name: str, session: AsyncSession
    ) -> List[Feedback]:
        """
        Retrieves a list of feedback entries by user_name.

        Parameters
        ----------
        user_name : str
            The username for which feedback entries are retrieved.
        session : AsyncSession
            The async database session.

        Returns
        -------
        List[Feedback]
            A list of feedback entries by the user.
        """
        query = select(FeedbackModel).where(FeedbackModel.user_name == user_name)
        result = await session.execute(query)
        feedback_list = result.scalars().all()

        return [
            Feedback.from_orm(feedback) for feedback in feedback_list
        ]  # Convert each ORM model to a Pydantic model

from typing import List
from uuid import UUID  # Import UUID here

from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import authenticate_key
from .schemas import Feedback, FeedbackResponse

router = APIRouter(
    dependencies=[Depends(authenticate_key)], tags=["Feedback endpoints"]
)

# In-memory storage for feedback (can be replaced with a database in production)
feedback_storage: List[Feedback] = []


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: Feedback) -> FeedbackResponse:
    """
    This endpoint allows users to submit feedback
    """

    feedback_storage.append(feedback)  # Save feedback in the in-memory storage
    return FeedbackResponse(feedback=feedback)


@router.get("/feedback/{chat_id}", response_model=FeedbackResponse)
async def get_feedback_by_chat_id(chat_id: UUID) -> FeedbackResponse:
    """
    This endpoint retrieves a single feedback entry by chat_id.
    Returns 400 when the feedback is not found.
    """
    # Find feedback by chat_id
    chat_feedback = next(
        (feedback for feedback in feedback_storage if feedback.chat_id == chat_id), None
    )

    if chat_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return FeedbackResponse(feedback=chat_feedback)


@router.get("/feedback/user/{user_id}", response_model=List[FeedbackResponse])
async def get_feedback_by_user_id(user_id: str) -> List[FeedbackResponse]:
    """
    This endpoint retrieves a list of feedback entries by user_id.
    Returns an empty list if no feedback is found.
    """
    # Find all feedback by user_id
    user_feedback = [
        feedback for feedback in feedback_storage if feedback.user_name == user_id
    ]

    if not user_feedback:
        raise HTTPException(status_code=404, detail="No feedback found for this user")

    return [FeedbackResponse(feedback=feedback) for feedback in user_feedback]

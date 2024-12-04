# feedback/routers.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import authenticate_user
from ..database import get_async_session
from ..services.FeedbackService import FeedbackService
from .schemas import FeedbackRequest, FeedbackResponse, ListFeedbackResponse

router = APIRouter(
    dependencies=[Depends(authenticate_user)], tags=["Feedback endpoints"]
)


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback_request: FeedbackRequest,
    session: AsyncSession = Depends(get_async_session),
) -> FeedbackResponse:
    """
    This endpoint allows users to submit feedback
    and saves it using the service layer.
    and saves it using the service layer.
    """
    try:
        saved_feedback = await FeedbackService.submit_feedback(
            feedback_request, session
        )
        return FeedbackResponse(feedback=saved_feedback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/feedback/{chat_id}", response_model=FeedbackResponse)
async def get_feedback_by_chat_id_route(
    chat_id: UUID, session: AsyncSession = Depends(get_async_session)
) -> FeedbackResponse:
    """
    This endpoint retrieves a single feedback entry by chat_id.
    Returns 404 when the feedback is not found.
    """
    feedback = await FeedbackService.retrieve_feedback_by_chat_id(chat_id, session)
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return FeedbackResponse(feedback=feedback)


@router.get("/feedback/user/{user_name}", response_model=ListFeedbackResponse)
async def get_feedback_by_user_name_route(
    user_name: str, session: AsyncSession = Depends(get_async_session)
) -> ListFeedbackResponse:
    """
    This endpoint retrieves a list of feedback entries by user_name.
    Returns an empty list if no feedback is found.
    """
    feedback_list = await FeedbackService.retrieve_feedback_by_user_name(
        user_name, session
    )
    return ListFeedbackResponse(feedbacks=feedback_list)

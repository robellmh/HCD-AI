from app.auth.dependencies import authenticate_either
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_session
from .models import Users
from .schemas import UserCreate, UserOut
from .utils import hash_password

TAG_METADATA = {
    "name": "User Management",
    "description": "Endpoints for adding, deleting and modifying users.",
}

router = APIRouter(
    dependencies=[Depends(authenticate_either)],
    tags=["User Management"],
)


@router.post("/users", response_model=UserOut)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserOut:
    """
    Create a new user.
    """
    try:
        assert user_data.role in ["admin", "user", None]
    except AssertionError:
        HTTPException(
            detail="Role must be either 'admin' or 'user' or left blank",
        )
    if user_data.role not in ["admin", "user", None]:
        raise HTTPException(
            status_code=400,
            detail="Role must be either 'admin' or 'user' or left blank",
        )
    hashed_password = await hash_password(user_data.password)
    new_user = Users(
        email=user_data.email, role=user_data.role, password=hashed_password
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return UserOut.model_validate(new_user)

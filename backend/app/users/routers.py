from app.auth.dependencies import authenticate_either
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
    prefix="/users",
)


@router.post("/create", response_model=UserOut)
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

    await session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    info = UserOut.model_validate(new_user)
    info.action_taken = "created"
    return info


@router.get("/get/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> UserOut:
    """
    Get a user by user_id.
    """
    result = await session.execute(select(Users).where(Users.user_id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user)


@router.post("/delete/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> UserOut:
    """
    Delete a user by user_id.
    """
    result = await session.execute(select(Users).where(Users.user_id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()
    info = UserOut.model_validate(user)
    info.action_taken = "deleted"
    return info

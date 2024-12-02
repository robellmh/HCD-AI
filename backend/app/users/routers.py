from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..auth.dependencies import authenticate_user
from ..database import get_async_session
from ..users.models import UsersDB
from ..users.schemas import RoleEnum
from .schemas import UserCreate, UserOut
from .utils import hash_password

TAG_METADATA = {
    "name": "User Management",
    "description": "Endpoints for adding, deleting and modifying users.",
}

router = APIRouter(
    dependencies=[Depends(authenticate_user)],
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
    if user_data.role not in RoleEnum.__members__:
        raise HTTPException(
            status_code=400,
            detail="Role must be either 'admin' or 'user' or left blank",
        )
    hashed_password = await hash_password(user_data.password)
    new_user = UsersDB(
        email=user_data.email, role=user_data.role, password=hashed_password
    )

    await session.add(new_user)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=400, detail="Email already registered. Context: " + str(e)
        ) from e
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
    result = await session.execute(select(UsersDB).where(UsersDB.user_id == user_id))
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
    Soft-delete a user by user_id, setting their is_archived flag to True.
    """
    result = await session.execute(select(UsersDB).where(UsersDB.user_id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_archived = True
    await session.commit()
    info = UserOut.model_validate(user)
    info.action_taken = "soft-deleted"
    return info

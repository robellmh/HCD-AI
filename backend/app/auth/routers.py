from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..auth.schemas import Token
from ..database import get_async_session
from ..users.models import UsersDB
from ..users.utils import verify
from .utils import create_access_token

router = APIRouter(tags=["Authentication"])

TAG_METADATA = {
    "name": "Authentication",
    "description": "Auth endpoints.",
}


@router.post("/login", response_model=Token)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    """
    Login to the application
    """
    result = await session.execute(
        select(UsersDB).where(UsersDB.email == user_credentials.username)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )
    if not await verify(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )
    access_token = await create_access_token(data={"user_id": user.user_id})
    return Token(access_token=access_token, token_type="bearer")

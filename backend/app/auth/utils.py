from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import get_async_session
from ..users.models import Users
from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET_KEY
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def create_access_token(data: dict) -> str:
    """
    Create a new access token with the given data."""
    to_encode = data.copy()

    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def verify_access_token(
    token: str, credentials_exception: HTTPException
) -> TokenData:
    """
    Verify the access token and return the token data."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = str(payload.get("user_id"))
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception from None

    return token_data


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
    role_check: Optional[str] = None,
) -> Users:
    """
    Get the current user from the access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = await verify_access_token(token, credentials_exception)

    statement = select(Users).filter(Users.user_id == token_data.user_id)
    result = await session.execute(statement)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    if role_check:
        if user.role != role_check:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required permissions",
            )
    return user

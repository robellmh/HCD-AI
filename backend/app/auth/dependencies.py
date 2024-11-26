from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import get_async_session
from ..users.models import Users
from .config import ALGORITHM, API_SECRET_KEY, JWT_SECRET_KEY

api_key_scheme = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


async def authenticate_either(
    token: str = Security(oauth2_scheme),
    credentials: HTTPAuthorizationCredentials = Security(api_key_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> Optional[Users]:
    """
    This dependency function authenticates users using either JWT or API key."""
    user: Optional[Users] = None
    # Try API Key authentication
    if credentials:
        api_key = credentials.credentials
        if api_key == API_SECRET_KEY:
            # Treat API key users as admin
            user = Users(user_id="api_key_user", role="admin")
            return user

    # Try JWT authentication
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            if user_id:
                result = await session.execute(
                    select(Users).where(Users.user_id == user_id)
                )
                user = result.scalars().first()
                if user:
                    return user
        except JWTError:
            pass

    # If authentication fails
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(user: Users = Depends(authenticate_either)) -> Users:
    """
    This dependency function retrieves the current user."""
    return user


async def require_admin(user: Users = Depends(authenticate_either)) -> Users:
    """
    This dependency function checks if the user is an admin."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user

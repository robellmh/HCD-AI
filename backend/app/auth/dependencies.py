import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import get_async_session
from ..users.models import Users
from ..utils import setup_logger
from .config import API_SECRET_KEY, JWT_ALGORITHM, JWT_SECRET_KEY

logger = setup_logger()

api_key_scheme = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


async def authenticate_either(
    token: str = Security(oauth2_scheme),
    credentials: HTTPAuthorizationCredentials = Security(api_key_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> Users | None:
    """
    Authenticate the user using either an API key or an access token.
    """
    if credentials:
        api_key = credentials.credentials
        if api_key == API_SECRET_KEY:
            user = Users(user_id="api_key_user", role="admin")
            return user

    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("user_id")
            if user_id:
                result = await session.execute(
                    select(Users).where(Users.user_id == user_id)
                )
                user = result.scalars().first()
                if user:
                    return user
        except jwt.PyJWTError as e:
            logger.warning(f"Token decoding failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(user: Users = Depends(authenticate_either)) -> Users:
    """
    Get the current user from the access token.
    """
    return user


async def require_admin(user: Users = Depends(authenticate_either)) -> Users:
    """
    Ensure the user is an admin.
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user

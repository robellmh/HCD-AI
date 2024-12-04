import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import get_async_session
from ..users.models import UsersDB
from ..users.schemas import RoleEnum
from ..utils import setup_logger
from .config import JWT_ALGORITHM, JWT_SECRET_KEY

logger = setup_logger()

api_key_scheme = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


async def authenticate_user(
    token: str = Security(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> UsersDB | None:
    """
    Authenticate the user using either an API key or an access token.
    """

    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("user_id")
            if user_id:
                result = await session.execute(
                    select(UsersDB).where(UsersDB.user_id == user_id)
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


async def require_admin(user: UsersDB = Depends(authenticate_user)) -> UsersDB:
    """
    Ensure the user is an admin.
    """
    if user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user

from asyncio import run

from app.database import get_async_session
from app.users.models import UsersDB
from app.users.utils import hash_password
from app.utils import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession

logger = setup_logger()


async def create_admin_user(email: str, password: str) -> None:
    """
    Add an admin user to the database.
    """
    session_generator = get_async_session()
    session: AsyncSession = await anext(session_generator)
    try:
        hashed_password = await hash_password(password)
        admin_user = UsersDB(
            email=email,
            hashed_password=hashed_password,
            role="admin",
            is_archived=False,
        )
        session.add(admin_user)
        await session.commit()
    finally:
        await session_generator.aclose()


if __name__ == "__main__":
    """
    Add an admin user to the database w/ default creds.
    """
    run(create_admin_user("admin@me.com", "pass123"))
    logger.info(
        """Admin user created
        Credentials:
        Email: admin@me.com
        Password: pass123"""
    )

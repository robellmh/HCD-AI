from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base, JSONDict
from .schemas import UserQuery


class UserQueryDB(Base):
    """
    User query database model
    """

    __tablename__ = "query"

    query_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, nullable=False
    )
    query_metadata: Mapped[JSONDict] = mapped_column(String, nullable=True)
    query_text: Mapped[str] = mapped_column(String, nullable=False)


async def save_query(query: UserQuery, asession: AsyncSession) -> UserQueryDB:
    """
    Save the query to the database
    """
    query_db = UserQueryDB(**query.model_dump())
    asession.add(query_db)
    await asession.commit()
    await asession.refresh(query_db)

    return query_db

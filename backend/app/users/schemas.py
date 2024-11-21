from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """
    Class representing the data required to create a new user.
    """

    email: str = Field(..., description="The email address of the new user.")
    password: str = Field(..., description="The password of the new user.")
    role: Optional[str] = Field(
        None, description="The role of the new user, if applicable."
    )


class UserOut(BaseModel):
    """
    Class representing the response model for a user.
    """

    user_id: int
    email: EmailStr
    created_at: datetime

    class Config:
        """
        Pydantic configuration for the UserOut model.
        """

        from_attributes = True


class UserLogin(BaseModel):
    """
    Class representing the data required to log in a user.
    """

    email: EmailStr
    password: str

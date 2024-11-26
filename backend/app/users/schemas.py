from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RoleEnum(str, Enum):
    """
    Enum representing the possible roles for a user.
    """

    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    """
    Class representing the data required to create a new user.
    """

    email: str = Field(..., description="The email address of the new user.")
    password: str = Field(..., description="The password of the new user.")
    role: RoleEnum = Field(..., description="The role of the new user.")


class UserOut(BaseModel):
    """
    Class representing the response model for a user.
    """

    user_id: int
    email: EmailStr
    created_at: datetime
    action_taken: Optional[str] = None

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

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class RoleEnum(str, Enum):
    """
    Enum for user roles.
    """

    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    """
    Base class for user schemas.
    """

    email: EmailStr = Field(..., description="The email address of the user.")
    role: RoleEnum = Field(..., description="The role of the user.")
    is_archived: bool = Field(False, description="Indicates if the user is archived.")


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """

    password: str = Field(..., description="The password of the new user.")


class UserOut(UserBase):
    """
    Schema for outputting user information.
    """

    user_id: int
    created_at: datetime
    action_taken: str

    class Config:
        """
        Configuration for the schema.
        """

        orm_mode = True


class UserLogin(BaseModel):
    """
    Schema for user login.
    """

    email: EmailStr
    password: str

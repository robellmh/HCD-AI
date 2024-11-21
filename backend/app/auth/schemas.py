from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    Class representing the token response model.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Class representing the token data model.
    """

    user_id: Optional[str] = None

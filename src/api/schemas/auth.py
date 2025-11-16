from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):

    """Data structure for auth token data."""

    access_token: str
    token_type: str = "bearer" # noqa: S105

class UserBase(BaseModel):

    """Data structure for core user information fields."""

    username: str
    email: Optional[str] = None

class UserInDB(UserBase):

    """"Data structure for ful user information fields."""

    id: int
    role: str = "user"

class UserResponse(UserInDB):

    """Data structure for user information with custom fields."""

    pass # будут еще поля

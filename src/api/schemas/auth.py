from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):

    """Data structure for auth token data."""

    access_token: str
    token_type: str = Field(default="bearer") # noqa: S105


class UserBase(BaseModel):

    """Data structure for core user information fields."""

    username: str = Field(..., min_length=5)
    email: EmailStr


class UserInDB(UserBase):

    """Data structure for ful user information fields."""

    id: UUID
    role: str = Field(default="user")


class UserResponse(UserInDB):

    """Data structure for user information with custom fields."""

    pass  # будут еще поля


class UserRegistration(UserBase):

    """Data structure for user registration process."""

    password: str = Field(..., min_length=8)

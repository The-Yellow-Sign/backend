from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRole(str, Enum):

    """Data structure for user's role names."""

    USER = "user"
    ADMIN = "admin"


class User(BaseModel):

    """Data structure for user information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    role: UserRole = UserRole.USER
    hashed_password: str
    email: Optional[EmailStr] = None


class Role(BaseModel):

    """Data structure for role."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: UserRole
    permissions: List[str]

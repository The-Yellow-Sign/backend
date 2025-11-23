from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):

    """Data structure for user information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[EmailStr] = None
    role: str
    hashed_password: str


class Role(BaseModel):

    """Data structure for role."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    permissions: List[str]

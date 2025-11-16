from typing import List, Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):

    """Data structure for user information."""

    id: int
    username: str
    email: Optional[EmailStr] = None
    role: str


class Role(BaseModel):

    """Data structure for role."""

    id: int
    name: str
    permissions: List[str]

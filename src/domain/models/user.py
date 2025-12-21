from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr


class User(BaseModel):

    """Data structure for user information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    username: str
    email: Optional[EmailStr] = None
    role: str
    hashed_password: str


class Role(BaseModel):

    """Data structure for role."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    permissions: List[str]

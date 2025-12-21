from typing import List

from pydantic import BaseModel, Field

from src.api.schemas.auth import UserBase


class RoleCreate(BaseModel):

    """Data structure for creating a new role."""

    name: str = Field(...)
    permissions: List[str] = Field(..., example=["read:repo:project_x", "chat:use"])

class UserRoleUpdate(BaseModel):

    """Data structure for updating role for existing user."""

    role: str = Field(..., example="admin")

class UserResponse(UserBase):

    """Data structure for information about user."""

    id: int
    role: str

from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.api.schemas.auth import UserBase


class RoleCreate(BaseModel):

    """Data structure for creating a new role."""

    name: str = Field(..., example="admin")
    permissions: List[str] = Field(..., example=["read:repo:project_x", "chat:use"])


class RoleResponse(BaseModel):

    """Data structure for information about role."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str = Field(..., example="admin")
    permissions: List[str] = Field(..., example=["read:repo:project_x", "chat:use"])


class UserRoleUpdate(BaseModel):

    """Data structure for updating role for existing user."""

    role: str = Field(..., example="admin")


class UserResponse(UserBase):

    """Data structure for information about user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str = Field(..., example="admin")


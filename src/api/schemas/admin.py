from typing import List

from pydantic import BaseModel, Field

from src.api.schemas.auth import UserBase


class RoleCreate(BaseModel):
    name: str = Field(...)
    permissions: List[str] = Field(..., example=["read:repo:project_x", "chat:use"])

class UserRoleUpdate(BaseModel):
    role: str = Field(..., example="admin")

class UserResponse(UserBase):
    id: int
    role: str

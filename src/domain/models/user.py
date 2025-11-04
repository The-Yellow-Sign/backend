from typing import List, Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    role: str


class Role(BaseModel):
    id: int
    name: str
    permissions: List[str]

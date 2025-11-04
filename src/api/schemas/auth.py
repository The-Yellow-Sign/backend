from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    
class UserInDB(UserBase):
    id: int
    role: str = "user"

class UserResponse(UserInDB):
    pass # будут езе поля

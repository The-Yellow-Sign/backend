from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

from src.api.schemas.chat import Source


class Message(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    sources: Optional[List[Source]] = None

class Chat(BaseModel):
    id: int
    title: str
    owner_id: int 
    created_at: datetime
    messages: List[Message] = []

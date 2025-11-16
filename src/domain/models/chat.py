from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.api.schemas.chat import Source


class Message(BaseModel):

    """Data structure for an existing LLM message."""

    id: int
    role: str
    content: str
    created_at: datetime
    sources: Optional[List[Source]] = None

class Chat(BaseModel):

    """Data structure fot chat response."""

    id: int
    title: str
    owner_id: int
    created_at: datetime
    messages: List[Message] = []

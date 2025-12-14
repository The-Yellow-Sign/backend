from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict


class Source(BaseModel):

    """Data structure for source."""

    title: str
    url: str
    quote: str | None = None

class Message(BaseModel):

    """Data structure for chat message."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    role: str
    content: str
    created_at: datetime
    sources: Optional[List[Source]] = None

class Chat(BaseModel):

    """Data structure for chat."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    owner_id: UUID4
    created_at: datetime
    messages: List[Message] = []

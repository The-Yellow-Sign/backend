from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class MessageRole(str, Enum):

    """Data structure for message's role names."""

    USER = "user"
    ASSISTANT = "assistant"


class Source(BaseModel):

    """Data structure for source."""

    model_config = ConfigDict(from_attributes=True)

    title: str
    url: HttpUrl
    quote: str


class Message(BaseModel):

    """Data structure for chat message."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    sources: Optional[List[Source]] = None


class Chat(BaseModel):

    """Data structure for chat."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime
    messages: Optional[List[Message]] = None

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class Source:

    """Data structure for source."""

    title: str
    url: str
    quote: str


@dataclass
class Message:

    """Data structure for chat message."""

    id: UUID
    role: str
    content: str
    created_at: datetime
    sources: Optional[List[Source]] = None


@dataclass
class Chat:

    """Data structure for chat."""

    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime
    messages: List[Message] = None

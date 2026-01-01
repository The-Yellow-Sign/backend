from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class Source:

    """Data structure for source."""

    title: str
    url: str
    quote: str


@dataclass
class Message:

    """Data structure for chat message."""

    id: UUID = uuid4()
    role: str = "assistant"
    content: str = ""
    created_at: datetime = datetime.now()
    sources: Optional[List[Source]] = None

    def __post_init__(self):
        if self.sources is None:
            self.sources = []


    def to_dict(self) -> dict:
        """Convert Message object to valid dictionary."""
        return {
            "id": str(self.id),
            "role": self.role,
            "content": self.content,
            "created_at": str(self.created_at),
            "sources": self.sources
        }


@dataclass
class Chat:

    """Data structure for chat."""

    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime
    messages: List[Message] = None

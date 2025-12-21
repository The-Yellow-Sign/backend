from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field


class SourceMeta(BaseModel):

    """Data structure for custom metafields. Can be used for filtering in retrieval scenario."""

    pass  # можно добавить кастомные поля для применения фильтрации при поиске


class Source(BaseModel):

    """Data structure for source information."""

    title: str
    url: str
    quote: str | None = None


class MessageBase(BaseModel):

    """Data structure for content in LLM messages."""

    content: str


class MessageCreate(MessageBase):

    """Data structure for creating LLM message."""

    pass


class MessageResponse(MessageBase):

    """Data structure for an existing LLM message."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    role: str = Field(..., example="user")
    created_at: datetime
    sources: Optional[List[Source]] = None  # только для assistant роли?


class ChatBase(BaseModel):

    """Data structure for chat title."""

    title: str


class ChatResponse(ChatBase):

    """Data structure fot chat response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    created_at: datetime
    owner_id: UUID4


class ChatHistoryResponse(ChatResponse):

    """Data structure for a full chat history with all messages."""

    messages: List[MessageResponse]

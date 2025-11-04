from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, UUID4


class SourceMeta(BaseModel):
    pass # можно добавить кастомные поля для применения фильтрации при поиске


class Source(BaseModel):
    document_title: str = Field(...)
    document_id: UUID4 = Field(...)
    repository_url: HttpUrl = Field(...)
    content: str = Field(...)
    metadata: SourceMeta = Field(...)


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    role: str = Field(..., example="user")
    created_at: datetime
    sources: Optional[List[Source]] = None # только для assistant роли?


class ChatBase(BaseModel):
    title: str


class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    owner_id: int


class ChatHistoryResponse(ChatResponse):
    messages: List[MessageResponse]

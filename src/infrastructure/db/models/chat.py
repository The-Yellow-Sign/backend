from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.infrastructure.db.models.base import Base


class Chat(Base):

    """ORM-model for Chat."""

    __tablename__ = "chats"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, title={self.title!r})"


class Message(Base):

    """ORM-model for Message."""

    __tablename__ = "messages"

    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))

    role: Mapped[str] = mapped_column(String(20), nullable=False) # "user" или "assistant"

    content: Mapped[str] = mapped_column(Text, nullable=False)

    sources: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chat: Mapped["Chat"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"Message(id={self.id!r}, role={self.role!r})"

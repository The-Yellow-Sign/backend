from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.chat import Chat as DomainChat, Message as DomainMessage
from src.domain.repositories.chat_repo import IChatRepository
from src.infrastructure.db.models.chat import Chat as ORMChat, Message as ORMMessage


class SqlAlchemyChatRepository(IChatRepository):

    """Chat's repository realisation for SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chat(self, owner_id: UUID4, title: str) -> DomainChat:
        """Create a new chat."""
        chat = ORMChat(owner_id=owner_id, title=title)
        self.session.add(chat)

        await self.session.flush()
        await self.session.refresh(chat)

        return DomainChat.model_validate(chat)

    async def get_user_chats(self, user_id: UUID4) -> List[DomainChat]:
        """Get all user chats by user_id."""
        stmt = select(ORMChat).where(ORMChat.owner_id == user_id).order_by(desc(ORMChat.created_at))
        result = await self.session.execute(stmt)
        chats = result.scalars().all()

        return [DomainChat.model_validate(c) for c in chats]

    async def get_chat_full(self, chat_id: UUID4) -> Optional[DomainChat]:
        """Get all chat messages by chat_id."""
        stmt = select(ORMChat).where(ORMChat.id == chat_id)
        result = await self.session.execute(stmt)
        chat = result.scalar_one_or_none()

        if chat:
            return DomainChat.model_validate(chat)

        return None

    async def add_message(
            self,
            chat_id: UUID4,
            role: str,
            content: str,
            sources: List[dict] = None
    ) -> DomainMessage:
        """Add new message to the chat."""
        msg = ORMMessage(
            chat_id=chat_id,
            role=role,
            content=content,
            sources=sources
        )
        self.session.add(msg)

        await self.session.flush()
        await self.session.refresh(msg)

        return DomainMessage.model_validate(msg)

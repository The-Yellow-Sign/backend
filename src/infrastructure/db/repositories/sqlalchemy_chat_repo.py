from typing import List, Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.chat import Chat as DomainChat, Message as DomainMessage
from src.domain.repositories.chat_repo import IChatRepository
from src.infrastructure.db.models.chat import Chat as ORMChat, Message as ORMMessage


class SqlAlchemyChatRepository(IChatRepository):

    """Chat's repository realisation for SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _transform_orm_model_to_domain(
            self,
            orm_model: ORMChat
    ) -> DomainChat:
        return DomainChat(
            id=orm_model.id,
            title=orm_model.title,
            owner_id=orm_model.owner_id,
            created_at=orm_model.created_at,
            messages=orm_model.messages
        )

    async def create_chat(self, owner_id: UUID, title: str) -> DomainChat:
        """Create a new chat."""
        chat = ORMChat(owner_id=owner_id, title=title)
        self.session.add(chat)

        await self.session.flush()
        await self.session.refresh(chat)

        return self._transform_orm_model_to_domain(chat)

    async def get_user_chats(self, user_id: UUID) -> List[DomainChat]:
        """Get all user chats by user_id."""
        stmt = select(ORMChat).where(ORMChat.owner_id == user_id).order_by(desc(ORMChat.created_at))
        result = await self.session.execute(stmt)
        chats = result.scalars().all()

        return [self._transform_orm_model_to_domain(chat) for chat in chats]

    async def get_chat_full(self, chat_id: UUID) -> Optional[DomainChat]:
        """Get all chat messages by chat_id."""
        stmt = select(ORMChat).where(ORMChat.id == chat_id)
        result = await self.session.execute(stmt)
        chat = result.scalar_one_or_none()

        if chat:
            return self._transform_orm_model_to_domain(chat)

        return None

    async def add_message(
            self,
            chat_id: UUID,
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

        return DomainMessage(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            sources=msg.sources
        )

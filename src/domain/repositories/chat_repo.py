from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.chat import Chat, Message


class IChatRepository(ABC):

    """Class sets the contract by which Application-layer connects with Infrastructure-layer."""

    @abstractmethod
    async def create_chat(self, owner_id: UUID, title: str) -> Chat:
        """Create a new chat."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_chats(self, user_id: UUID) -> List[Chat]:
        """Get all user chats by user_id."""
        raise NotImplementedError

    @abstractmethod
    async def get_chat_full(self, chat_id: UUID) -> Optional[Chat]:
        """Get all chat messages by chat_id."""
        raise NotImplementedError

    @abstractmethod
    async def add_message(
            self,
            chat_id: UUID,
            role: str,
            content: str,
            sources: List[dict] = None
    ) -> Message:
        """Add new message to the chat."""
        raise NotImplementedError

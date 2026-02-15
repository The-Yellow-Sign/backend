import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import UUID4

from src.domain.models.chat import Chat, Message, MessageRole, Source
from src.domain.repositories.cache_repo import ICacheRepository
from src.domain.repositories.chat_repo import IChatRepository


class ChatService:

    """Provides methods for chat service."""

    def __init__(
            self,
            chat_repo: IChatRepository,
            cache_repo: ICacheRepository
    ):
        self.chat_repo = chat_repo
        self.cache_repo = cache_repo

    async def create_chat(self, owner_id: UUID4, title: str) -> Chat:
        """Create a new chat with specified title for user by their id."""
        return await self.chat_repo.create_chat(owner_id, title)

    async def get_user_chats(self, user_id: UUID4) -> List[Chat]:
        """Get all user chats by user_id."""
        return await self.chat_repo.get_user_chats(user_id)

    async def get_chat_history(self, user_id: UUID4, chat_id: UUID4) -> Optional[Chat]:
        """Get chat history.

        1. Check that user has an access to this chat.
        2. Return chat history by its id.
        """
        chat = await self.chat_repo.get_chat_full(chat_id)
        await self._validate_chat_access(
            user_id=user_id,
            chat_id=chat_id,
            chat=chat
        )

        return chat

    async def _validate_chat_access(
            self,
            user_id: UUID4,
            chat_id: UUID4,
            chat: Optional[Chat] = None,
    ) -> Optional[Chat]:
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat {chat_id} not found"
            )

        if chat.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} doesn't have access to the chat {chat_id}."
            )

    async def ask_question(
            self,
            user_id: UUID4,
            chat_id: UUID4,
            repo_ids: List[UUID4],
            question: str
    ) -> Message:
        """QnA iteration.

        1. Check that user has an access to this chat.
        2. Save user's question.
        3. Run RAG pipeline (later).
        4. Save RAG answer.
        """
        chat = await self.chat_repo.get_chat_full(chat_id)
        await self._validate_chat_access(
            user_id=user_id,
            chat_id=chat_id,
            chat=chat
        )

        cache_key = self.cache_repo.construct_cache_key(
            query=question,
            repository_ids=repo_ids
        )

        message = await self.cache_repo.get_cached_value(cache_key)

        if message is None:
            message = Message(
                id=uuid.uuid4(),
                role=MessageRole.ASSISTANT,
                content="Will be a real llm call later :)",
                created_at=datetime.now(),
                sources=[
                    Source(
                        title="README.md",
                        url="https://gitlab/mock_project/readme/",
                        quote="Mock quote"
                    )
                ]
            )

            await self.cache_repo.put_cache_value(
                key=cache_key,
                message=message
            )

        await self.chat_repo.add_message(
            chat_id=chat_id,
            role="user",
            content=question
        )

        assistant_message = await self.chat_repo.add_message(
            chat_id=chat_id,
            role="assistant",
            content=message.content,
            sources=[source.model_dump(mode="json") for source in message.sources]
        )

        return assistant_message

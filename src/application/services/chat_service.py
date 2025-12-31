from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import UUID4

from src.domain.models.chat import Chat, Message
from src.domain.repositories.chat_repo import IChatRepository


class ChatService:

    """Provides methods for chat service."""

    def __init__(
            self,
            chat_repo: IChatRepository
    ):
        self.chat_repo = chat_repo

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

        return chat

    async def ask_question(
            self,
            user_id: UUID4,
            chat_id: UUID4,
            question: str
    ) -> Message:
        """QnA iteration.

        1. Check that user has an access to this chat.
        2. Save user's question.
        3. Run RAG pipeline (later).
        4. Save RAG answer.
        """
        chat = await self.chat_repo.get_chat_full(chat_id)
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

        await self.chat_repo.add_message(
            chat_id=chat_id,
            role="user",
            content=question
        )

        mock_answer = "Will be a real llm call later :)"
        mock_sources = [
            {
                "title": "README.md",
                "url": "http://gitlab/mock_project/readme",
                "quote": "Mock quote"
            }
        ]

        assistant_message = await self.chat_repo.add_message(
            chat_id=chat_id,
            role="assistant",
            content=mock_answer,
            sources=mock_sources
        )

        return assistant_message

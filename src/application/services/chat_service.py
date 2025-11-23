from src.domain.models.user import User


class ChatService:

    """Provides methods for chat service."""

    async def create_chat(self, user_id: int, title: str):
        """Create a new chat with specified title by user_id."""
        return {"id": 1, "title": title, "owner_id": user_id, "created_at": "..."}

    async def get_chats_for_user(self, user_id: int):
        """Get all created chats by user_id."""
        ...

    async def ask_question(self, user: User, chat_id: int, query: str):
        """Ask a question in specified chat.

        1. Check if this chat available to user
        2. Save user's message in database
        3. Find user's indexed repositories
        4. Run index search
        5. Run LLM answer generation
        6. Save response in database
        7. Return response to user.
        """
        return {
            "id": "valid uuid4",
            "role": "assistant",
            "content": "ответ на вопрос",
            "created_at": "datetime",
            "sources": [
                {
                    "document_title": "MOCK_README.md",
                    "repository_url": "https://gitlab.example.com/mock/repo",
                    "content": "... мок-цитата ...",
                }
            ],
        }

from src.domain.models.user import User


class ChatService:
    async def create_chat(self, user_id: int, title: str):
        return {"id": 1, "title": title, "owner_id": user_id, "created_at": "..."}

    async def get_chats_for_user(self, user_id: int):
        ...

    async def ask_question(self, user: User, chat_id: int, query: str):
        return {
            "id": "valid uuid4",
            "role": "assistant",
            "content": f"ответ на вопрос",
            "created_at": "datetime",
            "sources": [
                {
                    "document_title": "MOCK_README.md",
                    "repository_url": "https://gitlab.example.com/mock/repo",
                    "content": "... мок-цитата ..."
                }
            ]
        }

from typing import List

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status
from pydantic import UUID4

from src.api.dependencies import get_current_user
from src.api.schemas.chat import (
    ChatBase,
    ChatHistoryResponse,
    ChatResponse,
    MessageCreate,
    MessageResponse,
)
from src.application.services.chat_service import ChatService
from src.domain.models.user import User

router_chat = APIRouter(
    dependencies=[Depends(get_current_user)],
    route_class=DishkaRoute
)


@router_chat.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_chat(
        chat_data: ChatBase,
        service: FromDishka[ChatService],
        current_user: User = Depends(get_current_user)
):
    """Create new chat with a title."""
    return await service.create_chat(
        owner_id=current_user.id,
        title=chat_data.title
    )


@router_chat.get("/", response_model=List[ChatResponse])
async def get_user_chats(
        service: FromDishka[ChatService],
        current_user: User = Depends(get_current_user)
):
    """Get all chat for a specific user."""
    return await service.get_user_chats(current_user.id)


@router_chat.get("/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
        chat_id: UUID4,
        service: FromDishka[ChatService],
        current_user: User = Depends(get_current_user)
):
    """Get chat history by chat_id."""
    return await service.get_chat_history(
        user_id=current_user.id,
        chat_id=chat_id
    )


@router_chat.post(
    "/{chat_id}/message",
    response_model=MessageResponse,
)
async def send(
        chat_id: UUID4,
        message: MessageCreate,
        service: FromDishka[ChatService],
        current_user: User = Depends(get_current_user)
):
    """QnA iteration.

    1. Check that user has an access to this chat.
    2. Save user's question.
    3. Run RAG pipeline (later).
    4. Save RAG answer.
    """
    return await service.ask_question(
        user_id=current_user.id,
        chat_id=chat_id,
        question=message.content
    )

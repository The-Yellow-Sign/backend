from datetime import datetime
from typing import List

from fastapi import APIRouter, Body, Depends, status

from src.api.dependencies import get_current_user
from src.api.schemas.auth import UserInDB
from src.api.schemas.chat import (
    ChatBase,
    ChatHistoryResponse,
    ChatResponse,
    MessageCreate,
    MessageResponse,
    Source,
)

router_chat = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@router_chat.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_chat(
    title_body: ChatBase = Body(..., example={"title": "какое-то название чата"})
):
    ...

@router_chat.get("/", response_model=List[ChatResponse])
async def get_user_chats(current_user: UserInDB = Depends(get_current_user)):
    ...

@router_chat.get("/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(chat_id: int):
    ...

@router_chat.post(
    "/{chat_id}/message",
    response_model=MessageResponse,
)
async def post_message(chat_id: int, message: MessageCreate):
    fake_llm_response = MessageResponse(
        id=999,
        role="assistant",
        content="очень топовый ответ",
        created_at=datetime.now(),
        sources=[
            Source(
                document_title="DEPLOYMENT.md",
                repository_url="https://gitlab.example.com/project/repo",
                content="тут текст из мд файла"
            )
        ]
    )
    return fake_llm_response

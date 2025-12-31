from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.application.services.chat_service import ChatService
from src.domain.models.chat import Chat as DomainChat, Message as DomainMessage


@pytest.fixture(scope="function")
def mock_chat_repo():
    """Create AsyncMock for chat_repo."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_chat_success(mock_chat_repo):
    """Test that Chat is created."""
    owner_id = uuid4()
    title = "test_title"
    create_time = datetime.now()
    mock_chat_repo.create_chat.return_value = DomainChat(
        id=uuid4(),
        title=title,
        owner_id=owner_id,
        created_at=create_time
    )

    service = ChatService(mock_chat_repo)

    result = await service.create_chat(owner_id, title)

    mock_chat_repo.create_chat.assert_called_once_with(owner_id, title)

    assert result.title == title
    assert result.owner_id == owner_id
    assert result.created_at == create_time
    assert result.messages is None


@pytest.mark.asyncio
@pytest.mark.parametrize("n_chats", [0, 1, 2])
async def test_user_chats_success(mock_chat_repo, n_chats):
    """Test that all User's Chats are returned."""
    user_id = str(uuid4())
    mock_chat_repo.get_user_chats.return_value = [
        DomainChat(
            id=str(uuid4()),
            title=f"test_title_no{n_chats}",
            owner_id=user_id,
            created_at=datetime.now()
        )
    ] * n_chats

    service = ChatService(mock_chat_repo)

    result = await service.get_user_chats(user_id)

    mock_chat_repo.get_user_chats.assert_called_once_with(user_id)

    assert len(result) == n_chats


@pytest.mark.asyncio
async def test_get_chat_history_success(mock_chat_repo):
    """Test that all Chat history is returned."""
    user_id = uuid4()
    chat_id = uuid4()
    create_time = datetime.now()
    mock_chat_repo.get_chat_full.return_value = DomainChat(
        id=chat_id,
        title="test_title",
        owner_id=user_id,
        created_at=create_time
    )

    service = ChatService(mock_chat_repo)

    result = await service.get_chat_history(user_id=user_id, chat_id=chat_id)

    mock_chat_repo.get_chat_full.assert_called_once_with(chat_id)

    assert result.title == "test_title"
    assert result.owner_id == user_id
    assert result.created_at == create_time
    assert result.messages is None


@pytest.mark.asyncio
async def test_get_chat_history_chat_not_found(mock_chat_repo):
    """Test that error is raised when there is no Chat with specified chat_id."""
    mock_chat_repo.get_chat_full.return_value = None

    service = ChatService(mock_chat_repo)

    with pytest.raises(HTTPException) as exc:
        await service.get_chat_history(user_id=uuid4(), chat_id=uuid4())

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail


@pytest.mark.asyncio
async def test_get_chat_history_user_is_not_chat_owner(mock_chat_repo):
    """Test that error is raised when User doesn't own the exact Chat."""
    user_id = uuid4()
    chat_id = uuid4()
    mock_chat_repo.get_chat_full.return_value = DomainChat(
        id=chat_id,
        title="test_title",
        owner_id=user_id,
        created_at=datetime.now()
    )

    service = ChatService(mock_chat_repo)

    with pytest.raises(HTTPException) as exc:
        await service.get_chat_history(user_id=uuid4(), chat_id=chat_id)

    assert exc.value.status_code == 400
    assert "doesn't have access to the chat" in exc.value.detail


@pytest.mark.asyncio
async def test_get_ask_question_success(mock_chat_repo):
    """Test that new Messages are returned after QnA iteration."""
    user_id = uuid4()
    chat_id = uuid4()
    mock_chat_repo.get_chat_full.return_value = DomainChat(
        id=chat_id,
        title="test_title",
        owner_id=user_id,
        created_at=datetime.now()
    )

    question = "test_question"
    answer = "test_llm_answer"
    mock_chat_repo.add_message.side_effect = [
        DomainMessage(
            id=uuid4(),
            role="user",
            content=question,
            created_at=datetime.now()
        ),
        DomainMessage(
            id=uuid4(),
            role="assistant",
            content=answer,
            created_at=datetime.now()
        )
    ]
    service = ChatService(mock_chat_repo)

    result = await service.ask_question(
        user_id=user_id,
        chat_id=chat_id,
        question=question
    )

    assert mock_chat_repo.add_message.call_count == 2
    assert result.content == answer
    assert result.role == "assistant"


@pytest.mark.asyncio
async def test_get_ask_question_chat_not_found(mock_chat_repo):
    """Test that error is raised when there is no Chat with specified chat_id."""
    user_id = uuid4()
    chat_id = uuid4()
    mock_chat_repo.get_chat_full.return_value = None

    service = ChatService(mock_chat_repo)

    with pytest.raises(HTTPException) as exc:
        await service.ask_question(
            user_id=user_id,
            chat_id=chat_id,
            question="test_question"
        )

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail


@pytest.mark.asyncio
async def test_get_ask_question_user_is_not_chat_owner(mock_chat_repo):
    """Test that error is raised when User doesn't own the exact Chat."""
    user_id = uuid4()
    chat_id = uuid4()
    mock_chat_repo.get_chat_full.return_value = DomainChat(
        id=chat_id,
        title="test_title",
        owner_id=user_id,
        created_at=datetime.now()
    )

    service = ChatService(mock_chat_repo)

    with pytest.raises(HTTPException) as exc:
        await service.ask_question(
            user_id=uuid4(),
            chat_id=chat_id,
            question="test_question"
        )

    assert exc.value.status_code == 400
    assert "doesn't have access to the chat" in exc.value.detail

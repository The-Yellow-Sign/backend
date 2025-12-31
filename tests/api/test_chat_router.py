from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import HTTPException, status
from httpx import ASGITransport, AsyncClient

from src.api.dependencies import (
    get_current_user,
)
from src.application.services.chat_service import ChatService
from src.domain.models.chat import Chat as DomainChat, Message as DomainMessage
from src.domain.models.user import User as DomainUser

BASE_URL = "/v1/chat"


@pytest_asyncio.fixture
def mock_chat_service():
    """Create mock for ChatSevice."""
    service = AsyncMock(spec=ChatService)
    return service


@pytest.fixture
def mock_user():
    """Create mock for User."""
    return DomainUser(
        id=uuid4(),
        username="user",
        email="user@test.com",
        role="user",
        hashed_password="hash"
    )


@pytest_asyncio.fixture(scope="function")
async def dishka_app(app_fixture, mock_chat_service):
    """Fixture for Dishka integration."""
    provider = Provider()

    provider.provide(
        lambda: mock_chat_service,
        scope=Scope.APP,
        provides=ChatService
    )

    container = make_async_container(provider)
    app_fixture.middleware_stack = None
    setup_dishka(container, app_fixture)

    yield app_fixture

    await container.close()


@pytest_asyncio.fixture(scope="function")
async def ac(dishka_app, mock_user):
    """Create AsyncClient for tests."""
    dishka_app.dependency_overrides[get_current_user] = lambda: mock_user

    async with AsyncClient(transport=ASGITransport(app=dishka_app), base_url="http://test") as c:
        yield c

    dishka_app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_create_new_chat_success(ac, mock_chat_service, mock_user):
    """Test that endpoint returns new Chat when valid title provided."""
    chat_id = uuid4()
    chat_title = "test_title"

    payload = {
        "title": chat_title
    }

    mock_chat_service.create_chat.return_value = DomainChat(
        id=chat_id,
        title="test_title",
        owner_id=mock_user.id,
        created_at=datetime.now(),
        messages=[]
    )

    response = await ac.post(f"{BASE_URL}/", json=payload)

    mock_chat_service.create_chat.assert_called_once_with(
        owner_id=mock_user.id, title=chat_title
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "test_title"
    assert data["owner_id"] == str(mock_user.id)


@pytest.mark.asyncio
async def test_create_new_chat_no_title(ac):
    """Test that endpoint raises error when no title is provided."""
    response = await ac.post(f"{BASE_URL}/", json={}) # no title key in json

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user_chats_success(ac, mock_chat_service, mock_user):
    """Test that endpoint returns all user's Chats."""
    chat1 = DomainChat(
        id=uuid4(),
        title="test_title1",
        owner_id=mock_user.id,
        created_at=datetime.now(),
        messages=[]
    )
    chat2 = DomainChat(
        id=uuid4(),
        title="test_title2",
        owner_id=mock_user.id,
        created_at=datetime.now(),
        messages=[]
    )

    mock_chat_service.get_user_chats.return_value = [chat1, chat2]

    response = await ac.get(f"{BASE_URL}/")

    assert response.status_code == 200
    mock_chat_service.get_user_chats.assert_called_once_with(mock_user.id)

    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == str(chat1.id)
    assert data[0]["title"] == "test_title1"
    assert data[1]["id"] == str(chat2.id)
    assert data[1]["title"] == "test_title2"


@pytest.mark.asyncio
async def test_get_user_chats_empty(ac, mock_chat_service, mock_user):
    """Test that endpoint returns empty list when there is no user's Chats."""
    mock_chat_service.get_user_chats.return_value = []

    response = await ac.get(f"{BASE_URL}/")

    assert response.status_code == 200
    mock_chat_service.get_user_chats.assert_called_once_with(mock_user.id)

    assert response.json() == []


@pytest.mark.asyncio
async def test_get_chat_history_success(ac, mock_chat_service, mock_user):
    """Test that endpoint returns new Chat history."""
    chat_id = uuid4()

    message = DomainMessage(
        id=uuid4(),
        role="user",
        content="test_content",
        created_at=datetime.now()
    )

    chat_with_history = DomainChat(
        id=chat_id,
        title="test_title1",
        owner_id=mock_user.id,
        created_at=datetime.now(),
        messages=[message]
    )

    mock_chat_service.get_chat_history.return_value = chat_with_history

    response = await ac.get(f"{BASE_URL}/{chat_id}")

    assert response.status_code == 200
    mock_chat_service.get_chat_history.assert_called_once_with(
        user_id=mock_user.id, chat_id=chat_id
    )

    data = response.json()
    assert data["id"] == str(chat_id)
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "test_content"


@pytest.mark.asyncio
async def test_get_chat_history_not_found(ac, mock_chat_service):
    """Test that endpoint raises error when chat is not found."""
    chat_id = uuid4()

    mock_chat_service.get_chat_history.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Chat {chat_id} not found"
    )

    response = await ac.get(f"{BASE_URL}/{chat_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_send_message_success(ac, mock_chat_service, mock_user):
    """Test that endpoint returns the answer to the question (message) sent."""
    chat_id = uuid4()
    question = "test_question"

    payload = {"content": question}

    assistant_response = DomainMessage(
        id=uuid4(),
        role="assistant",
        content="test_answer",
        created_at=datetime.now()
    )
    mock_chat_service.ask_question.return_value = assistant_response

    response = await ac.post(f"{BASE_URL}/{chat_id}/message", json=payload)

    assert response.status_code == 200
    mock_chat_service.ask_question.assert_called_once_with(
        user_id=mock_user.id,
        chat_id=chat_id,
        question=question
    )

    data = response.json()
    assert data["role"] == "assistant"
    assert data["content"] == "test_answer"


from uuid import uuid4

import pytest
import pytest_asyncio
from pydantic import UUID4

from src.domain.models.chat import Chat as DomainChat
from src.domain.models.user import User as DomainUser
from src.infrastructure.db.repositories.sqlalchemy_chat_repo import SqlAlchemyChatRepository
from src.infrastructure.db.repositories.sqlalchemy_user_repo import SqlAlchemyUserRepository


@pytest.fixture(scope="function")
def user_repo(session):
    """Return SqlAlchemyUserRepository's fixture for tests."""
    return SqlAlchemyUserRepository(session)


@pytest.fixture(scope="function")
def chat_repo(session):
    """Return SqlAlchemyChatRepository's fixture for tests."""
    return SqlAlchemyChatRepository(session)


@pytest_asyncio.fixture(scope="function")
async def user_factory(user_repo):
    """Create User for tests.

    If specific values are not provided, factory creates a user with unique values.
    """

    async def _create_user(
        username: str = "default_user",
        email: str = "default@test.com",
        role: str = "user",
        hashed_password: str = "secret_hash"
    ) -> DomainUser:

        unique_suffix = str(uuid4())

        if username == "default_user":
            username = f"user_{unique_suffix}"
        if email == "default@test.com":
            email = f"user_{unique_suffix}@test.com"

        new_user_data = DomainUser(
            id=uuid4(),
            username=username,
            email=email,
            role=role,
            hashed_password=hashed_password
        )

        return await user_repo.create(new_user_data)

    return _create_user


@pytest_asyncio.fixture(scope="function")
async def test_user(user_factory):
    """Create user in db."""
    user = await user_factory(username="fixed_user", email="fixed@test.com")
    return user


@pytest_asyncio.fixture(scope="function")
async def chat_factory(chat_repo):
    """Create Chat for tests.

    If specific values are not provided, factory creates a chat with unique values.
    """

    async def _create_chat(
        title: str = "default_title",
        owner_id: UUID4 = uuid4()
    ) -> DomainChat:

        unique_suffix = str(uuid4())

        if title == "default_title":
            title = f"title_{unique_suffix}"

        return await chat_repo.create_chat(owner_id, title)

    return _create_chat


@pytest.mark.asyncio
async def test_create_chat_success(chat_factory, test_user):
    """Test that Chat is created."""
    title = "test_title"

    created_chat = await chat_factory(
        title=title,
        owner_id=test_user.id
    )

    assert created_chat.id is not None
    assert created_chat.title == title
    assert created_chat.owner_id == test_user.id


@pytest.mark.asyncio
@pytest.mark.parametrize("n_chats", [1, 2])
async def test_get_user_chats_success(chat_factory, chat_repo, test_user, n_chats):
    """Test that all User's Chats can be extracted by user_id."""
    title = f"test_title_{n_chats}"

    for _ in range(n_chats):
        await chat_factory(
            title=title,
            owner_id=test_user.id
        )

    all_chats = await chat_repo.get_user_chats(test_user.id)

    assert len(all_chats) == n_chats
    for ind in range(n_chats):
        assert all_chats[ind].id is not None
        assert all_chats[ind].owner_id == test_user.id
        assert all_chats[ind].title == f"test_title_{n_chats}"


@pytest.mark.asyncio
async def test_get_user_chats_empty_chat_list(chat_repo, test_user):
    """Test that an empty list will be returned when there is no Chats."""
    all_chats = await chat_repo.get_user_chats(test_user.id)

    assert all_chats == []


@pytest.mark.asyncio
async def test_add_message_success(chat_repo, chat_factory, test_user):
    """Test that Message is added."""
    chat = await chat_factory(owner_id=test_user.id)

    role = "user"
    content = "test_content"

    message = await chat_repo.add_message(
        chat_id=chat.id,
        role=role,
        content=content,
        sources=[]
    )

    assert message.id is not None
    assert message.role == role
    assert message.content == content
    assert message.sources == []


@pytest.mark.asyncio
async def test_get_chat_full_success(chat_repo, chat_factory, test_user):
    """Test that Message is added and can be extracted from Chat history."""
    chat = await chat_factory(owner_id=test_user.id)

    await chat_repo.add_message(chat.id, "user", "question1")
    await chat_repo.add_message(chat.id, "assistant", "answer1")

    full_chat = await chat_repo.get_chat_full(chat.id)

    assert full_chat is not None
    assert full_chat.id == chat.id

    assert len(full_chat.messages) == 2

    assert full_chat.messages[0].role == "user"
    assert full_chat.messages[0].content == "question1"
    assert full_chat.messages[1].role == "assistant"
    assert full_chat.messages[1].content == "answer1"


@pytest.mark.asyncio
async def test_get_chat_full_chat_not_found(chat_repo):
    """Test that nothing can be extracted from an unexisting Chat."""
    result = await chat_repo.get_chat_full(uuid4())

    assert result is None

from uuid import uuid4

import pytest
import pytest_asyncio

from src.domain.models.user import User as DomainUser
from src.infrastructure.db.repositories.sqlalchemy_user_repo import SqlAlchemyUserRepository


@pytest.fixture(scope="function")
def repo(session):
    """Return SqlAlchemyUserRepository's fixture for tests."""
    return SqlAlchemyUserRepository(session)


@pytest_asyncio.fixture(scope="function")
async def user_factory(repo):
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

        return await repo.create(new_user_data)

    return _create_user


@pytest.mark.asyncio
async def test_create_user_success(user_factory):
    """Test that User is created."""
    username="test_username1"
    email="test_email1@test.com"
    role="user"
    hashed_password="test_hash1"

    created_user = await user_factory(
        username=username,
        email=email,
        role=role,
        hashed_password=hashed_password
    )

    assert created_user.id is not None
    assert created_user.username == username
    assert created_user.email == email
    assert created_user.role == role
    assert created_user.hashed_password == hashed_password


@pytest.mark.asyncio
async def test_create_the_same_email_twice(repo, user_factory):
    """Test that User is not created if email is already used."""
    first_user = await user_factory(email="integ1@test.com")

    assert first_user.id is not None

    second_user = await user_factory(email="integ1@test.com")

    assert second_user is None


@pytest.mark.asyncio
async def test_create_the_same_username_twice(repo, user_factory):
    """Test that User is not created if username is already used."""
    first_user = await user_factory(username="integ_test_name1")

    assert first_user.id is not None

    second_user = await user_factory(username="integ_test_name1")

    assert second_user is None


@pytest.mark.asyncio
async def test_create_and_get_user_by_email_success(repo, user_factory):
    """Test that existing User can be extracted by email."""
    created_user = await user_factory(email="integ@test.com")

    assert created_user.id is not None

    fetched_user = await repo.get_by_email("integ@test.com")

    assert fetched_user == created_user


@pytest.mark.asyncio
async def test_create_and_get_user_by_email_not_found(repo, user_factory):
    """Test that User cannot be extracted by email if it doesnt exist."""
    created_user = await user_factory()

    assert created_user.id is not None

    fetched_user = await repo.get_by_email("ghost@test.com")

    assert fetched_user is None


@pytest.mark.asyncio
async def test_create_and_get_user_by_username_success(repo, user_factory):
    """Test that existing User can be extracted by username."""
    created_user = await user_factory(username="integ_test_name1")

    assert created_user.id is not None

    fetched_user = await repo.get_by_username(username="integ_test_name1")

    assert fetched_user == created_user


@pytest.mark.asyncio
async def test_create_and_get_user_by_username_not_found(repo, user_factory):
    """Test that User cannot be extracted by username if it doesnt exist."""
    created_user = await user_factory()

    assert created_user.id is not None

    fetched_user = await repo.get_by_username(username="ghost")

    assert fetched_user is None


@pytest.mark.asyncio
async def test_create_and_get_user_by_id_success(repo, user_factory):
    """Test that existing User can be extracted by id."""
    created_user = await user_factory(username="test_by_id")

    assert created_user.id is not None

    fetched_user = await repo.get_by_id(user_id=created_user.id)

    assert fetched_user == created_user


@pytest.mark.asyncio
async def test_create_and_get_user_by_id_not_found(repo, user_factory):
    """Test that User cannot be extracted by id if it doesnt exist."""
    created_user = await user_factory(username="test_by_id")

    assert created_user.id is not None

    fetched_user = await repo.get_by_id(user_id=uuid4())

    assert fetched_user is None


@pytest.mark.asyncio
@pytest.mark.parametrize("n_users", [1, 2, 3])
async def test_create_and_get_all_users_success(repo, user_factory, n_users):
    """Test that all existing Users can be extracted."""
    created_users = []
    for _ in range(n_users):
        created_users.append(
            await user_factory()
        )

    result = await repo.get_all_users()

    assert result == created_users


@pytest.mark.asyncio
async def test_create_and_get_all_users_empty(repo):
    """Test that an empty list is returned if there are no Users."""
    result = await repo.get_all_users()

    assert result == []


@pytest.mark.asyncio
async def test_update_user_success(repo, user_factory):
    """Test that all User's fields can be updated."""
    created_user = await user_factory()

    update_data = DomainUser(
        id=created_user.id,
        username="new_username",
        email="new_email@test.com",
        role="admin",
        hashed_password="new_hash"
    )

    updated_user = await repo.update(update_data)

    assert updated_user == update_data

    updated_user_from_db = await repo.get_by_id(updated_user.id)

    assert updated_user_from_db == updated_user # check that db contains new values


@pytest.mark.asyncio
async def test_update_user_not_found(repo, user_factory):
    """Test that there won't be any updates if user doen't exist."""
    await user_factory()

    update_data = DomainUser(
        id=uuid4(),
        username="new_username",
        email="new_email@test.com",
        role="admin",
        hashed_password="new_hash"
    )

    updated_user = await repo.update(update_data)

    assert updated_user is None


@pytest.mark.asyncio
async def test_update_user_value_already_used(repo, user_factory):
    """Test that values that are already used cannot be provided in update operations."""
    created_user1 = await user_factory(username="username1")

    await user_factory(username="username2")

    update_data = DomainUser(
        id=created_user1.id,
        username="username2", # already used!
        email="new_email@test.com",
        role="admin",
        hashed_password="new_hash"
    )

    updated_user = await repo.update(update_data)

    assert updated_user is None

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api.schemas.auth import UserRegistration
from src.application.services.auth_service import AuthService
from src.domain.models.user import User as DomainUser


@pytest.fixture(scope="function")
def mock_user_repo():
    """Create AsyncMock for user_repo."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_register_new_user_success(mock_user_repo, mocker):
    """Test that new service returns created User if username and email are unique."""
    fixed_uuid = str(uuid4())
    hashed_password = "test_hash"
    mocker.patch("passlib.context.CryptContext.hash", return_value=hashed_password)
    mocker.patch("src.infrastructure.db.models.base.uuid.uuid4", return_value=fixed_uuid)

    mock_user_repo.get_by_username.return_value = None
    mock_user_repo.get_by_email.return_value = None
    new_user = UserRegistration(
        username="test_username",
        email="test@test.com",
        password="test_password"
    )
    created_user = DomainUser(
        id=fixed_uuid,
        username="test_username",
        email="test@test.com",
        role="user",
        hashed_password=hashed_password
    )
    mock_user_repo.create.return_value = created_user

    service = AuthService(mock_user_repo)

    result = await service.register_new_user(new_user)

    mock_user_repo.get_by_username.assert_called_once_with("test_username")
    mock_user_repo.get_by_email.assert_called_once_with("test@test.com")
    assert result == created_user


@pytest.mark.asyncio
async def test_resgister_new_user_username_already_exist(mock_user_repo):
    """Test that new service raises error when user with the same username already exists."""
    new_user = UserRegistration(
        username="test_username",
        email="test@test.com",
        password="test_password"
    )

    mock_user_repo.get_by_username.return_value = DomainUser(
        id=str(uuid4()),
        username="test_username",
        email="different@test.com",
        role="user",
        hashed_password="test_hash"
    )

    service = AuthService(mock_user_repo)

    with pytest.raises(HTTPException) as exc:
        await service.register_new_user(new_user)

    mock_user_repo.get_by_email.assert_not_called()

    assert exc.value.status_code == 400
    assert "Username is already registered" in exc.value.detail


@pytest.mark.asyncio
async def test_resgister_new_user_email_already_exist(mock_user_repo):
    """Test that new service raises error when user with the same email already exists."""
    new_user = UserRegistration(
        username="test_username",
        email="test@test.com",
        password="test_password"
    )

    mock_user_repo.get_by_username.return_value = None
    mock_user_repo.get_by_email.return_value = DomainUser(
        id=str(uuid4()),
        username="different_username",
        email="test@test.com",
        role="user",
        hashed_password="test_hash"
    )

    service = AuthService(mock_user_repo)

    with pytest.raises(HTTPException) as exc:
        await service.register_new_user(new_user)


    assert exc.value.status_code == 400
    assert "Email is already registered" in exc.value.detail


@pytest.mark.asyncio
async def test_resgister_new_user_error_create(mock_user_repo):
    """Test that new service raises error when registration fails."""
    new_user = UserRegistration(
        username="test_username",
        email="test@test.com",
        password="test_password"
    )

    mock_user_repo.get_by_username.return_value = None
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = None

    service = AuthService(mock_user_repo)

    with pytest.raises(HTTPException) as exc:
        await service.register_new_user(new_user)


    assert exc.value.status_code == 400
    assert "User could not be created" in exc.value.detail


@pytest.mark.asyncio
async def test_authenticate_user_success(mock_user_repo, mocker):
    """Test that new service returns token and its type when username and password are valid."""
    username = "test_username"
    password = "test_password"
    hash_pass = "test_password_hashed"
    mocker.patch("passlib.context.CryptContext.hash", return_value=hash_pass)
    mocker.patch("passlib.context.CryptContext.verify", return_value=True)
    user_in_db = DomainUser(
        id=str(uuid4()),
        username=username,
        email="test@test.com",
        role="user",
        hashed_password=hash_pass
    )
    mock_user_repo.get_by_username.return_value = user_in_db

    service = AuthService(mock_user_repo)

    result = await service.authenticate_user(
        username=username,
        password=password
    )

    mock_user_repo.get_by_username.assert_called_once_with(username)
    assert "access_token" in result
    assert result["token_type"] == "bearer"
    assert len(result) == 2


@pytest.mark.asyncio
async def test_authenticate_user_user_not_found(mock_user_repo):
    """Test that service raises error when User is not found."""
    mock_user_repo.get_by_username.return_value = None

    service = AuthService(mock_user_repo)

    with pytest.raises(HTTPException) as exc:
        await service.authenticate_user(
            username="test_username",
            password="test_password"
        )

    mock_user_repo.get_by_username.assert_called_once_with("test_username")

    assert exc.value.status_code == 401
    assert "Incorrect username" in exc.value.detail


@pytest.mark.asyncio
async def test_authenticate_user_incorrect_password(mock_user_repo, mocker):
    """Test that service raises error when password is not correct."""
    username = "test_username"
    password = "test_password"
    hash_pass = "test_password_hashed"
    mocker.patch("passlib.context.CryptContext.hash", return_value="incorrect_hash")
    mocker.patch("passlib.context.CryptContext.verify", return_value=False)
    user_in_db = DomainUser(
        id=str(uuid4()),
        username=username,
        email="test@test.com",
        role="user",
        hashed_password=hash_pass
    )
    mock_user_repo.get_by_username.return_value = user_in_db

    service = AuthService(mock_user_repo)

    with pytest.raises(HTTPException) as exc:
        await service.authenticate_user(
            username=username,
            password=password
        )

    mock_user_repo.get_by_username.assert_called_once_with(username)

    assert exc.value.status_code == 401
    assert "Incorrect username or password" in exc.value.detail

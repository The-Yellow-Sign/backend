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
from src.application.services.auth_service import AuthService
from src.domain.models.user import User as DomainUser

BASE_URL = "/v1/auth"


@pytest_asyncio.fixture
def mock_auth_service():
    """Create mock for AuthSevice."""
    service = AsyncMock(spec=AuthService)
    return service


@pytest_asyncio.fixture(scope="function")
async def dishka_app(app_fixture, mock_auth_service):
    """Fixture for Dishka integration."""
    provider = Provider()

    provider.provide(
        lambda: mock_auth_service,
        scope=Scope.APP,
        provides=AuthService
    )

    container = make_async_container(provider)
    app_fixture.middleware_stack = None
    setup_dishka(container, app_fixture)

    yield app_fixture

    await container.close()


@pytest_asyncio.fixture(scope="function")
async def ac(dishka_app):
    """Create AsyncClient for tests."""
    dishka_app.dependency_overrides[get_current_user] = lambda: DomainUser(
        id=uuid4(),
        username="username",
        email="user@test.com",
        role="user",
        hashed_password="hash"
    )

    async with AsyncClient(transport=ASGITransport(app=dishka_app), base_url="http://test") as c:
        yield c

    dishka_app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_register_user_success(ac, mock_auth_service):
    """Test that endpoint returns register_data that have been provided."""
    register_data = {
        "username": "test_username",
        "email": "test@test.com",
        "password": "test_password",
    }

    expected_user = DomainUser(
        id=uuid4(),
        username=register_data["username"],
        email=register_data["email"],
        role="user",
        hashed_password="test_hash"
    )
    mock_auth_service.register_new_user.return_value = expected_user

    response = await ac.post(f"{BASE_URL}/register", json=register_data)

    assert response.status_code == 200

    mock_auth_service.register_new_user.assert_called_once()

    data = response.json()
    assert data["username"] == register_data["username"]
    assert data["email"] == register_data["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_login_for_access_token_success(ac, mock_auth_service):
    """Test that endpoint returns JWT-token and its type if valid login_data provided."""
    login_data = {
        "username": "test_username",
        "password": "test_password"
    }

    token_response = {
        "access_token": "test_jwt_token",
        "token_type": "bearer"
    }
    mock_auth_service.authenticate_user.return_value = token_response

    response = await ac.post(f"{BASE_URL}/token", data=login_data)

    assert response.status_code == 200

    mock_auth_service.authenticate_user.assert_called_once_with(
        username="test_username", password="test_password"
    )

    data = response.json()
    assert data["access_token"] == "test_jwt_token"
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_for_access_token_not_all_fields(ac, mock_auth_service):
    """Test that endpoint raises error when not all login data fields provided."""
    token_response = {
        "access_token": "test_jwt_token",
        "token_type": "bearer"
    }
    mock_auth_service.authenticate_user.return_value = token_response

    login_data = {
        "password": "test_password"
    }

    response = await ac.post(f"{BASE_URL}/token", data=login_data)

    assert response.status_code == 422

    login_data = {
        "username": "test_username"
    }

    response = await ac.post(f"{BASE_URL}/token", data=login_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_credentials(ac, mock_auth_service):
    """Test that endpoint raises error when login data is incorrect."""
    mock_auth_service.authenticate_user.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )

    login_data = {
        "username": "test_username",
        "password": "test_password"
    }
    response = await ac.post(f"{BASE_URL}/token", data=login_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_users_me_success(ac):
    """Test that endpoint returns valid data of current user."""
    response = await ac.get(f"{BASE_URL}/me")

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "username" # from override fixture
    assert data["email"] == "user@test.com"

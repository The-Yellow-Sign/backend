from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import HTTPException, status
from httpx import ASGITransport, AsyncClient

from src.api.dependencies import get_current_admin_user
from src.application.services.admin_service import AdminService
from src.domain.models.user import Role as DomainRole, User as DomainUser, UserRole

BASE_URL = "/v1/admin"


@pytest_asyncio.fixture
def mock_admin_service():
    """Create mock for AdminSevice."""
    service = AsyncMock(spec=AdminService)
    return service


@pytest_asyncio.fixture(scope="function")
async def dishka_app(app_fixture, mock_admin_service):
    """Fixture for Dishka integration."""
    provider = Provider()

    provider.provide(
        lambda: mock_admin_service,
        scope=Scope.APP,
        provides=AdminService
    )

    container = make_async_container(provider)
    app_fixture.middleware_stack = None
    setup_dishka(container, app_fixture)

    yield app_fixture

    await container.close()


@pytest_asyncio.fixture(scope="function")
async def ac(dishka_app):
    """Create AsyncClient for tests."""
    dishka_app.dependency_overrides[get_current_admin_user] = lambda: DomainUser(
        id=uuid4(),
        username="admin",
        email="admin@test.com",
        role="admin",
        hashed_password="hash"
    )

    async with AsyncClient(transport=ASGITransport(app=dishka_app), base_url="http://test") as c:
        yield c

    dishka_app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_all_users_not_empty(ac, mock_admin_service):
    """Test that endpoint returns a list of Users when there is a valid data."""
    mock_users_list = [
        DomainUser(
            id=uuid4(),
            username="user1",
            email="u1@t.com",
            role="user",
            hashed_password=".."
        ),
        DomainUser(
            id=uuid4(),
            username="user2",
            email="u2@t.com",
            role="user",
            hashed_password=".."
        ),
    ]
    mock_admin_service.get_all_users.return_value = mock_users_list

    response = await ac.get(f"{BASE_URL}/users")

    mock_admin_service.get_all_users.assert_called_once()
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "user1"
    assert data[0]["role"] == "user"
    assert data[1]["username"] == "user2"
    assert data[1]["role"] == "user"


@pytest.mark.asyncio
async def test_get_all_users_empty(ac, mock_admin_service):
    """Test that endpoint returns an empty list when there is no data."""
    mock_admin_service.get_all_users.return_value = []

    response = await ac.get(f"{BASE_URL}/users")

    mock_admin_service.get_all_users.assert_called_once()
    assert response.status_code == 200

    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_get_all_roles_not_empty(ac, mock_admin_service):
    """Test that endpoint returns a list of Role when there is a valid data."""
    mock_roles_list = [
        DomainRole(id=uuid4(), name=UserRole.USER, permissions=["perm1"]),
        DomainRole(id=uuid4(), name=UserRole.ADMIN, permissions=["perm2"]),
    ]
    mock_admin_service.get_all_roles.return_value = mock_roles_list

    response = await ac.get(f"{BASE_URL}/roles")

    mock_admin_service.get_all_roles.assert_called_once()
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "user"
    assert data[0]["permissions"] == ["perm1"]
    assert data[1]["name"] == "admin"
    assert data[1]["permissions"] == ["perm2"]


@pytest.mark.asyncio
async def test_get_all_roles_empty(ac, mock_admin_service):
    """Test that endpoint returns an empty list when there is no data."""
    mock_admin_service.get_all_roles.return_value = []

    response = await ac.get(f"{BASE_URL}/roles")

    mock_admin_service.get_all_roles.assert_called_once()
    assert response.status_code == 200

    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_update_user_role_success(ac, mock_admin_service):
    """Test that endpoint returns User with updated fields when there is a valid data."""
    new_role = "user"
    user_id = uuid4()
    mock_admin_service.update_user_role.return_value = DomainUser(
        id=user_id,
        username="test_username",
        email="test_email@test.com",
        role=new_role,
        hashed_password="test_hash"
    )

    payload = {"role": new_role}
    response = await ac.put(f"{BASE_URL}/users/{user_id}/role", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(user_id)
    assert data["role"] == new_role

    mock_admin_service.update_user_role.assert_called_once_with(user_id, new_role)


@pytest.mark.asyncio
async def test_update_user_role_invalid_body(ac, mock_admin_service):
    """Test that endpoint returns error when there is no valid data."""
    user_id = uuid4()

    response = await ac.put(f"{BASE_URL}/users/{user_id}/role", json={})
    assert response.status_code == 422

    response = await ac.put(f"{BASE_URL}/users/{user_id}/role", json={"wrong_field": "admin"})
    assert response.status_code == 422

    mock_admin_service.update_user_role.assert_not_called()


@pytest.mark.asyncio
async def test_create_new_role_success(ac, mock_admin_service):
    """Test that endpoint returns new Role with when there is a valid data."""
    payload = {
        "name": "user",
        "permissions": ["test_permissions"]
    }

    role_response = DomainRole(
        id=uuid4(),
        name=payload["name"],
        permissions=payload["permissions"]
    )
    mock_admin_service.create_new_role.return_value = role_response

    response = await ac.post(f"{BASE_URL}/roles", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["permissions"] == payload["permissions"]
    assert "id" in data

    mock_admin_service.create_new_role.assert_called_once()

    args, _ = mock_admin_service.create_new_role.call_args
    assert args[0].name == payload["name"]


@pytest.mark.asyncio
async def test_create_new_role_invalid_body(ac, mock_admin_service):
    """Test that endpoint returns error when there is no valid data."""
    payload = {
        "permissions": ["read"]
    }

    response = await ac.post(f"{BASE_URL}/roles", json=payload)
    assert response.status_code == 422


    response = await ac.post(f"{BASE_URL}/roles", json={})
    assert response.status_code == 422

    mock_admin_service.create_new_role.assert_not_called()


@pytest.mark.asyncio
async def test_create_new_role_already_exists(ac, mock_admin_service):
    """Test that endpoint returns error when Role already exists."""
    payload = {"name": "existing_role", "permissions": []}

    mock_admin_service.create_new_role.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Role already exists"
    )

    response = await ac.post(f"{BASE_URL}/roles", json=payload)

    assert response.status_code == 400

    mock_admin_service.create_new_role.assert_called_once()

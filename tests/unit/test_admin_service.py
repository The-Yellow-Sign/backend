from dataclasses import replace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api.schemas.admin import RoleCreate
from src.application.services.admin_service import AdminService
from src.domain.models.user import Role as DomainRole, User as DomainUser


@pytest.fixture(scope="function")
def mock_user_repo():
    """Create AsyncMock for user_repo."""
    return AsyncMock()


@pytest.fixture(scope="function")
def mock_role_repo():
    """Create AsyncMock for role_repo."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_all_users_not_empty(mock_user_repo, mock_role_repo):
    """Test that service returns list of Users when db contains valid data."""
    existing_users = [
        DomainUser(
            id=uuid4(),
            username="test1",
            email="test1@test.com",
            role="user",
            hashed_password="..."
        ),
        DomainUser(
            id=uuid4(),
            username="test2",
            email="test2@test.com",
            role="user",
            hashed_password="..."
        )
    ]

    mock_user_repo.get_all_users.return_value = existing_users
    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    result = await service.get_all_users()

    mock_user_repo.get_all_users.assert_called_once()
    assert result == existing_users


@pytest.mark.asyncio
async def test_get_all_users_empty(mock_user_repo, mock_role_repo):
    """Test that service returns empty list when db is empty."""
    mock_user_repo.get_all_users.return_value = []

    mock_user_repo.get_all_users.return_value = []
    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    result = await service.get_all_users()

    mock_user_repo.get_all_users.assert_called_once()
    assert result == []


@pytest.mark.asyncio
async def test_get_all_roles_not_empty(mock_user_repo, mock_role_repo):
    """Test that service returns list of Roles when db contains valid data."""
    roles = [
        DomainRole(id=uuid4(), name="test_role1", permissions=["read:repo:project_x"]),
        DomainRole(id=uuid4(), name="test_role2", permissions=["chat:use"])
    ]
    mock_role_repo.get_all_roles.return_value = roles

    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    result = await service.get_all_roles()

    mock_role_repo.get_all_roles.assert_called_once()
    assert result == roles


@pytest.mark.asyncio
async def test_get_all_roles_empty(mock_user_repo, mock_role_repo):
    """Test that service returns empty list when db is empty."""
    mock_role_repo.get_all_roles.return_value = []

    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    result = await service.get_all_roles()

    mock_role_repo.get_all_roles.assert_called_once()
    assert result == []


@pytest.mark.asyncio
async def test_update_user_role_success(mock_user_repo, mock_role_repo):
    """Test that service updates Role with valid data when User exists."""
    user_id = uuid4()
    existing_user = DomainUser(
        id=user_id,
        username="test",
        email="test@test.com",
        role="user",
        hashed_password="..."
    )
    mock_user_repo.get_by_id.return_value = existing_user

    role_name = "admin"
    mock_role_repo.get_by_name.return_value = DomainRole(
        id=uuid4(), name="admin", permissions=[]
    )

    existing_user = replace(existing_user, **{"role": role_name})
    mock_user_repo.update.return_value = existing_user
    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    result = await service.update_user_role(user_id=user_id, role_name=role_name)

    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    mock_role_repo.get_by_name.assert_called_once_with(role_name)

    called_user_obj = mock_user_repo.update.call_args[0][0]
    assert called_user_obj.role == role_name

    assert result.role == role_name


@pytest.mark.asyncio
async def test_update_user_role_user_doesnt_exist(mock_user_repo, mock_role_repo):
    """Test that service doesn't update Role when User doesn't exist."""
    mock_user_repo.get_by_id.return_value = None

    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    user_id = uuid4()
    with pytest.raises(HTTPException) as exc:
        await service.update_user_role(user_id, "admin")

    mock_user_repo.get_by_id.assert_called_once()
    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    assert exc.value.status_code == 400
    assert "no such user" in exc.value.detail


@pytest.mark.asyncio
async def test_update_user_role_role_doesnt_exist(mock_user_repo, mock_role_repo):
    """Test that service doesn't update Role when Role doesn't exist."""
    user_id = uuid4()
    existing_user = DomainUser(
        id=user_id,
        username="test",
        email="test@test.com",
        role="user",
        hashed_password="..."
    )
    mock_user_repo.get_by_id.return_value = existing_user

    mock_role_repo.get_by_name.return_value = None

    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    role_name = "admin"
    with pytest.raises(HTTPException) as exc:
        await service.update_user_role(user_id, role_name)

    mock_user_repo.get_by_id.assert_called_once()
    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    mock_role_repo.get_by_name.assert_called_once()
    mock_role_repo.get_by_name.assert_called_once_with(role_name)
    assert exc.value.status_code == 400
    assert "no such role" in exc.value.detail


@pytest.mark.asyncio
async def test_create_new_role_success(
    mock_user_repo,
    mock_role_repo,
    mocker
):
    """Test that new Role is created when there is valid data."""
    role_name = "admin"
    permissions = ["read:repo:project_x", "chat:use"]
    fixed_uuid = uuid4()
    new_role = DomainRole(
        id=fixed_uuid,
        name=role_name,
        permissions=permissions
    )

    mocker.patch("src.infrastructure.db.models.base.uuid.uuid4", return_value=fixed_uuid)
    mock_role_repo.get_by_name.return_value = None
    mock_role_repo.create.return_value = new_role

    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    result = await service.create_new_role(
        RoleCreate(
            name=role_name,
            permissions=permissions
        )
    )

    mock_role_repo.get_by_name.assert_called_once()
    mock_role_repo.get_by_name.assert_called_once_with(role_name)
    mock_role_repo.create.assert_called_once()
    assert result == new_role


@pytest.mark.asyncio
async def test_create_new_role_role_already_exists(
    mock_user_repo,
    mock_role_repo
):
    """Test that new Role isn't created when the same Role already exists."""
    role_name = "admin"
    permissions = ["read:repo:project_x", "chat:use"]

    mock_role_repo.get_by_name.return_value = DomainRole(
        id=uuid4(),
        name=role_name,
        permissions=permissions
    )

    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    with pytest.raises(HTTPException) as exc:
        await service.create_new_role(
            RoleCreate(
                name=role_name,
                permissions=permissions
            )
        )

    mock_role_repo.get_by_name.assert_called_once()
    mock_role_repo.get_by_name.assert_called_once_with(role_name)
    assert exc.value.status_code == 400
    assert "Role already exists" in exc.value.detail


@pytest.mark.asyncio
async def test_create_new_role_error(
    mock_user_repo,
    mock_role_repo
):
    """Test that new Role isn't created when there is an error."""
    role_name = "admin"
    permissions = ["read:repo:project_x", "chat:use"]

    mock_role_repo.get_by_name.return_value = None
    mock_role_repo.create.return_value = None

    service = AdminService(user_repo=mock_user_repo, role_repo=mock_role_repo)

    with pytest.raises(HTTPException) as exc:
        await service.create_new_role(
            RoleCreate(
                name=role_name,
                permissions=permissions
            )
        )

    mock_role_repo.get_by_name.assert_called_once()
    mock_role_repo.get_by_name.assert_called_once_with(role_name)
    mock_role_repo.create.assert_called_once()
    assert exc.value.status_code == 400
    assert "Error creating a new role" in exc.value.detail

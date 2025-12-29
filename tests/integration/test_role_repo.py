from uuid import uuid4

import pytest

from src.domain.models.user import Role as DomainRole
from src.infrastructure.db.repositories.sqlalchemy_role_repo import SqlAlchemyRoleRepository


@pytest.fixture(scope="function")
def role_repo(session):
    """Return SqlAlchemyRoleRepository's fixture for tests."""
    return SqlAlchemyRoleRepository(session)


@pytest.mark.asyncio
async def test_create_role_success(role_repo):
    """Test that Role is created."""
    role_name = "test_role"
    permissions = ["test1", "test2"]
    new_role = DomainRole(
        id=uuid4(),
        name=role_name,
        permissions=permissions
    )

    saved_role = await role_repo.create(new_role)

    assert saved_role is not None
    assert saved_role.name == role_name
    assert saved_role.permissions == permissions
    assert saved_role.id is not None


@pytest.mark.asyncio
async def test_create_role_duplicate_name(role_repo):
    """Test that Role is not created if it already exists."""
    role1 = DomainRole(
        id=uuid4(),
        name="test_role1",
        permissions=[]
    )
    await role_repo.create(role1)

    role2 = DomainRole(
        id=uuid4(),
        name="test_role1", # the same name
        permissions=["other_perm"]
    )

    result = await role_repo.create(role2)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_name_success(role_repo):
    """Test that Role is extracted by name."""
    name = "test_name"
    permissions = ["test_perm"]
    await role_repo.create(
        DomainRole(id=uuid4(), name=name, permissions=permissions)
    )

    found_role = await role_repo.get_by_name(name)

    assert found_role is not None
    assert found_role.name == name
    assert found_role.permissions == permissions


@pytest.mark.asyncio
async def test_get_by_name_not_found(role_repo):
    """Test that Role is not extracted if it isn't exist."""
    result = await role_repo.get_by_name("test_role")
    assert result is None


@pytest.mark.asyncio
async def test_get_all_roles_success(role_repo):
    """Test that all Roles are extracted."""
    roles_to_create = ["test_1", "test_2", "test_3"]
    for name in roles_to_create:
        await role_repo.create(
            DomainRole(id=uuid4(), name=name, permissions=[])
        )

    all_roles = await role_repo.get_all_roles()

    assert len(all_roles) == 3

    fetched_names = [r.name for r in all_roles]
    for name in roles_to_create:
        assert name in fetched_names


@pytest.mark.asyncio
async def test_get_all_roles_empty(role_repo):
    """Test that an empty list is extracted if there are no Roles."""
    all_roles = await role_repo.get_all_roles()

    assert all_roles == []

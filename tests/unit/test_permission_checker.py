import uuid

import pytest
from fastapi import HTTPException

from src.api.dependencies import PermissionChecker
from src.core.security_policy import Action
from src.domain.models.user import User, UserRole


@pytest.fixture(scope="session")
def user():
    """Create a fixture for user."""
    return User(
        id=uuid.uuid4(),
        username="test_username",
        role=UserRole.USER,
        hashed_password="..",
        email="test@test.com"
    )


@pytest.fixture(scope="session")
def admin():
    """Create a fixture for admin."""
    return User(
        id=uuid.uuid4(),
        username="test_username",
        role=UserRole.ADMIN,
        hashed_password="..",
        email="test@test.com"
    )


def test_access_allowed(admin):
    """Test that PermissionChecker doesn't raise and error if user has an access."""
    checker = PermissionChecker(Action.ADMIN_ACCESS)

    checker(admin)


def test_access_denied(user):
    """Test that PermissionChecker raises and error if user doesn't have an access."""
    checker = PermissionChecker(Action.ADMIN_ACCESS)

    with pytest.raises(HTTPException):
        checker(user)

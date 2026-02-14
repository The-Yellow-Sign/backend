from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from httpx import ASGITransport, AsyncClient

from src.api.dependencies import get_current_user
from src.application.services.index_service import IndexService
from src.domain.models.user import User as DomainUser

BASE_URL = "/v1/repository"


@pytest_asyncio.fixture
def mock_index_service():
    """Create mock for IndexSevice."""
    service = AsyncMock(spec=IndexService)
    return service


@pytest_asyncio.fixture(scope="function")
async def dishka_app(app_fixture, mock_index_service):
    """Fixture for Dishka integration."""
    provider = Provider()

    provider.provide(
        lambda: mock_index_service,
        scope=Scope.APP,
        provides=IndexService
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
        username="admin",
        email="admin@test.com",
        role="admin",
        hashed_password="hash"
    )

    async with AsyncClient(transport=ASGITransport(app=dishka_app), base_url="http://test") as c:
        yield c

    dishka_app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_configure_gitlab_success(ac, mock_index_service, mocker):
    """Test that endpoint returns ok message when config is configured."""
    mocker.patch(
        "src.application.services.index_service.encrypt_data",
        side_effect=lambda x: f"encrypted_{x}"
    )
    payload = {
        "url": "https://gitlab.example.com",
        "private_token": "secret-token-123"
    }

    mock_response = {"status": "ok", "message": "GitLab configuration saved successfully."}
    mock_index_service.configure_gitlab.return_value = mock_response

    response = await ac.post(f"{BASE_URL}/config", json=payload)

    assert response.status_code == 202
    assert response.json() == mock_response

    mock_index_service.configure_gitlab.assert_called_once_with(
        url="https://gitlab.example.com/",
        private_token="secret-token-123"
    )


@pytest.mark.asyncio
async def test_list_gitlab_repositories_success(ac, mock_index_service):
    """Test that endpoint returns list of Repositories."""
    mock_repos = [
        {
            "id": str(uuid4()),
            "name": "Repo 1",
            "path_with_namespace": "group/repo1",
            "url": "https://gitlab.com/group/repo1"
        },
        {
            "id": str(uuid4()),
            "name": "Repo 2",
            "path_with_namespace": "group/repo2",
            "url": "https://gitlab.com/group/repo2"
        }
    ]
    mock_index_service.list_repositories.return_value = mock_repos

    response = await ac.get(f"{BASE_URL}/list")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Repo 1"
    assert data[0]["path_with_namespace"] == "group/repo1"
    assert data[1]["name"] == "Repo 2"
    assert data[1]["path_with_namespace"] == "group/repo2"

    mock_index_service.list_repositories.assert_called_once()


@pytest.mark.asyncio
async def test_list_gitlab_repositories_empty(ac, mock_index_service):
    """Test that endpoint returns empty list when there are no repositories."""
    mock_index_service.list_repositories.return_value = []

    response = await ac.get(f"{BASE_URL}/list")

    assert response.status_code == 200
    assert response.json() == []

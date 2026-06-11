from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from httpx import ASGITransport, AsyncClient

from src.api.dependencies import get_current_user
from src.application.services.admin_service import AdminService
from src.application.services.index_service import IndexService
from src.domain.models.knowledge import JobStatus
from src.domain.models.user import User as DomainUser

BASE_URL = "/v1/indexing"


@pytest_asyncio.fixture
def mock_admin_service():
    """Create mock for AdminSevice."""
    service = AsyncMock(spec=AdminService)
    return service


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
async def test_trigger_indexing_success(ac, mock_index_service):
    """Test that endpoint returns created indexing_job."""
    repo_ids = [str(uuid4())]
    payload = {"repository_ids": repo_ids}

    job_id = str(uuid4())
    mock_job_response = {
        "id": job_id,
        "status": JobStatus.RUNNING.value,
        "repository_ids": repo_ids,
        "created_at": datetime.now(),
        "details": "run"
    }
    mock_index_service.trigger_indexing.return_value = mock_job_response

    response = await ac.post(f"{BASE_URL}/trigger", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == job_id
    assert data["status"] == JobStatus.RUNNING.value
    assert str(data["repository_ids"][0]) == repo_ids[0]


@pytest.mark.asyncio
async def test_delete_indexing_job_success(ac, mock_index_service):
    """Test that endpoint deletes existing indexing_job."""
    job_id = str(uuid4())
    mock_index_service.delete_indexind_job.return_value = True

    response = await ac.delete(f"{BASE_URL}/{job_id}")

    assert response.status_code == 200
    assert response.json() is True

    mock_index_service.delete_indexind_job.assert_called_once_with(job_id)


@pytest.mark.asyncio
async def test_delete_indexing_job_not_found(ac, mock_index_service):
    """Test that endpoint cannot delete indexing_job that doesn't exist."""
    job_id = str(uuid4())
    mock_index_service.delete_indexind_job.return_value = False

    response = await ac.delete(f"{BASE_URL}/{job_id}")

    assert response.status_code == 200
    assert response.json() is False


@pytest.mark.asyncio
async def test_get_indexing_status_success(ac, mock_index_service):
    """Test that endpoint returns the status of indexing_job."""
    job_id = str(uuid4())
    mock_job_response = {
        "id": job_id,
        "status": JobStatus.RUNNING.value,
        "repository_ids": [],
        "created_at": datetime.now(),
        "details": "run"
    }
    mock_index_service.get_indexing_status.return_value = mock_job_response

    response = await ac.get(f"{BASE_URL}/status/{job_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == job_id
    assert data["status"] == JobStatus.RUNNING.value

    mock_index_service.get_indexing_status.assert_called_once_with(job_id)


@pytest.mark.asyncio
async def test_update_indexing_status_success(ac, mock_index_service):
    """Test that endpoint updated status of an existing indexing_job."""
    job_id = str(uuid4())

    payload = {
        "status": JobStatus.SUCCESS.value,
        "details": "done"
    }

    mock_job_response = {
        "id": job_id,
        "status": JobStatus.SUCCESS.value,
        "repository_ids": [],
        "created_at": datetime.now(),
        "details": "done"
    }
    mock_index_service.update_indexing_status.return_value = mock_job_response

    response = await ac.put(f"{BASE_URL}/status/{job_id}", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == JobStatus.SUCCESS.value
    assert data["details"] == "done"

    assert mock_index_service.update_indexing_status.call_count == 1
    args = mock_index_service.update_indexing_status.call_args
    assert args[0][0] == job_id
    assert args[0][1].status == JobStatus.SUCCESS.value


@pytest.mark.asyncio
async def test_update_indexing_status_not_found(ac, mock_index_service):
    """Test that endpoint returns error when indexing_job doesn't exist."""
    job_id = str(uuid4())
    payload = {"status": JobStatus.FAILED.value}

    mock_index_service.update_indexing_status.return_value = None

    response = await ac.put(f"{BASE_URL}/status/{job_id}", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == f"Job with id {job_id} not found"

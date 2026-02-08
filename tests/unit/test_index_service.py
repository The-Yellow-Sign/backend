from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api.schemas.repository import JobStatusUpdate
from src.application.services.index_service import IndexService
from src.domain.models.knowledge import (
    GitLabConfig as DomainGitLabConfig,
    IndexingJob,
    JobStatus,
    Repository,
)


@pytest.fixture(scope="function")
def mock_gitlab_repo():
    """Create AsyncMock for gitlab_repo."""
    return AsyncMock()


@pytest.fixture(scope="function")
def mock_job_repo():
    """Create AsyncMock for job_repo."""
    return AsyncMock()


@pytest.fixture
def gitlab_config():
    """Create mock fot DomainGitLabConfig."""
    return DomainGitLabConfig(
        id=1,
        url="https://test.com",
        private_token_encrypted="encrypted_test_token"
    )


@pytest.fixture
def repository():
    """Create mock fot Repository."""
    return Repository(
        id=uuid4(),
        name="test_repository",
        path_with_namespace="test1/test2",
        url="https://test.com"
    )


@pytest.fixture
def indexing_job(repository):
    """Create mock fot IndexingJob."""
    return IndexingJob(
        id=uuid4(),
        status=JobStatus.RUNNING,
        repository_ids=[repository.id],
        created_at=datetime.now()
    )

@pytest.mark.asyncio
async def test_configure_gitlab_success(
        mock_gitlab_repo,
        mock_job_repo,
        gitlab_config,
        mocker
):
    """Test that ok message is returned when config is configured."""
    mocker.patch(
        "src.application.services.index_service.encrypt_data",
        side_effect=lambda x: f"encrypted_{x}"
    )
    mock_gitlab_repo.save_config.return_value = gitlab_config
    service = IndexService(mock_gitlab_repo, mock_job_repo)

    result = await service.configure_gitlab("test_url", "test_token")

    mock_gitlab_repo.save_config.assert_called_once_with("test_url", "encrypted_test_token")
    assert result == {"status": "ok", "message": "GitLab configuration saved successfully."}


@pytest.mark.asyncio
async def test_list_repositories_success(
        mock_gitlab_repo,
        mock_job_repo,
        gitlab_config,
        repository,
        mocker
):
    """Test that service returns list of existing repositories."""
    mock_gitlab_repo.get_config.return_value = gitlab_config
    mock_gitlab_repo.gitlab_client.list_projects.return_value = [repository]
    mocker.patch(
        "src.application.services.index_service.decrypt_data",
        side_effect=lambda x: f"decrypted_{x}"
    )
    service = IndexService(mock_gitlab_repo, mock_job_repo)

    mock_client = AsyncMock()
    mock_client.list_projects.return_value = [repository]
    service.gitlab_client = mock_client

    result = await service.list_repositories()

    mock_gitlab_repo.get_config.assert_called_once()
    service.gitlab_client.list_projects.assert_called_once()
    assert result == [repository]


@pytest.mark.asyncio
async def test_list_repositories_success_empty_repository_list(
        mock_gitlab_repo,
        mock_job_repo,
        gitlab_config,
        repository,
        mocker
):
    """Test that service returns an empty list when there are no existing repositories."""
    mock_gitlab_repo.get_config.return_value = gitlab_config
    mock_gitlab_repo.gitlab_client.list_projects.return_value = [repository]
    mocker.patch(
        "src.application.services.index_service.decrypt_data",
        side_effect=lambda x: f"decrypted_{x}"
    )
    service = IndexService(mock_gitlab_repo, mock_job_repo)

    mock_client = AsyncMock()
    mock_client.list_projects.return_value = []
    service.gitlab_client = mock_client

    result = await service.list_repositories()

    mock_gitlab_repo.get_config.assert_called_once()
    service.gitlab_client.list_projects.assert_called_once()
    assert result == []


@pytest.mark.asyncio
async def test_list_repositories_config_not_found(
        mock_gitlab_repo,
        mock_job_repo
):
    """Test that service returns error when config is not configured."""
    mock_gitlab_repo.get_config.return_value = None
    service = IndexService(mock_gitlab_repo, mock_job_repo)

    with pytest.raises(HTTPException) as exc:
       await service.list_repositories()

    mock_gitlab_repo.get_config.assert_called_once()
    assert exc.value.status_code == 404
    assert exc.value.detail == "GitLab is not configured yet. Please add config first."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "job_status",
    [
        JobStatus.FAILED,
        JobStatus.PENDING,
        JobStatus.RUNNING,
        JobStatus.SUCCESS
    ]
)
async def test_trigger_indexing_success(
        mock_gitlab_repo,
        mock_job_repo,
        gitlab_config,
        repository,
        indexing_job,
        mocker,
        job_status
):
    """Test that service creates job with specified status."""
    mock_gitlab_repo.get_config.return_value = gitlab_config
    mocker.patch(
        "src.application.services.index_service.decrypt_data",
        side_effect=lambda x: f"decrypted_{x}"
    )

    indexing_job.status = job_status
    mock_job_repo.create_job.return_value = indexing_job
    service = IndexService(mock_gitlab_repo, mock_job_repo)

    mock_client = AsyncMock()
    mock_client.trigger_indexing.return_value = indexing_job
    service.mlops_client = mock_client

    result = await service.trigger_indexing([repository.id])

    mock_gitlab_repo.get_config.assert_called_once()
    mock_client.trigger_indexing.assert_called_once_with(
        repo_ids=[repository.id],
        gitlab_url=gitlab_config.url,
        gitlab_token="decrypted_encrypted_test_token"
    )
    mock_job_repo.create_job.assert_called_once_with(
        job_id=indexing_job.id,
        repo_ids=[repository.id],
        status=indexing_job.status,
        details=None
    )
    assert result == indexing_job


@pytest.mark.asyncio
async def test_delete_indexing_job_success(
        mock_gitlab_repo,
        mock_job_repo,
        indexing_job
):
    """Test that service delete an existing indexing_job."""
    ok_message = {
        "status": "ok",
        "message": f"Job {indexing_job.id} has been deleted successfully."
    }
    mock_job_repo.delete_job.return_value = True

    service = IndexService(mock_gitlab_repo, mock_job_repo)

    result = await service.delete_indexind_job(indexing_job.id)

    mock_job_repo.delete_job.assert_called_once_with(indexing_job.id)
    assert result == ok_message


@pytest.mark.asyncio
async def test_delete_indexing_job_doesnt_exist(
        mock_gitlab_repo,
        mock_job_repo,
        indexing_job
):
    """Test that service returns error message when indexing_job doesn't exist."""
    error_message = {
        "status": "error",
        "message": f"Job {indexing_job.id} doesn't exist."
    }
    mock_job_repo.delete_job.return_value = False

    service = IndexService(mock_gitlab_repo, mock_job_repo)

    result = await service.delete_indexind_job(indexing_job.id)

    mock_job_repo.delete_job.assert_called_once_with(indexing_job.id)
    assert result == error_message


@pytest.mark.asyncio
async def test_get_indexing_status_success(
        mock_gitlab_repo,
        mock_job_repo,
        indexing_job
):
    """Test that service returns indexing_job with specified id."""
    mock_job_repo.get_job.return_value = indexing_job

    service = IndexService(mock_gitlab_repo, mock_job_repo)

    result = await service.get_indexing_status(indexing_job.id)

    mock_job_repo.get_job.assert_called_once_with(indexing_job.id)
    assert result == indexing_job


@pytest.mark.asyncio
async def test_get_indexing_status_job_not_found(
        mock_gitlab_repo,
        mock_job_repo,
        indexing_job
):
    """Test that service returnsNone when indexing_job doesn't exist."""
    mock_job_repo.get_job.return_value = None

    service = IndexService(mock_gitlab_repo, mock_job_repo)
    result = await service.get_indexing_status(indexing_job.id)

    mock_job_repo.get_job.assert_called_once_with(indexing_job.id)
    assert result is None


@pytest.mark.ayncio
@pytest.mark.parametrize(
    "job_status",
    [
        JobStatus.FAILED,
        JobStatus.PENDING,
        JobStatus.RUNNING,
        JobStatus.SUCCESS
    ]
)
async def test_update_indexing_status_success(
        mock_gitlab_repo,
        mock_job_repo,
        indexing_job,
        job_status
):
    """Test that service updates indexing_job's status."""
    update_data = JobStatusUpdate(
        status=job_status
    )

    indexing_job.status = job_status
    mock_job_repo.update_job_status.return_value = indexing_job

    service = IndexService(mock_gitlab_repo, mock_job_repo)

    result = await service.update_indexing_status(
        job_id=indexing_job.id,
        status_update=update_data
    )

    assert result == indexing_job

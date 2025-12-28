from typing import List, Optional
from uuid import uuid4

import pytest
import pytest_asyncio
from pydantic import UUID4

from src.domain.models.knowledge import IndexingJob as DomainIndexingJob, JobStatus
from src.infrastructure.db.repositories.sqlalchemy_job_repo import SqlAlchemyJobRepository


@pytest.fixture(scope="function")
def job_repo(session):
    """Return SqlAlchemyJobRepository's fixture for tests."""
    return SqlAlchemyJobRepository(session)


@pytest_asyncio.fixture(scope="function")
async def job_factory(job_repo):
    """Create Job for tests.

    If specific values are not provided, factory creates a job with unique values.
    """

    async def _create_indexing_job(
        job_id: str = uuid4(),
        status: JobStatus = JobStatus.RUNNING,
        repository_ids: Optional[List[UUID4]] = None,
        details: Optional[str] = None
    ) -> DomainIndexingJob:
        if repository_ids is None:
            repository_ids = []

        return await job_repo.create_job(
            job_id=job_id,
            repo_ids=repository_ids,
            status=status,
            details=details
        )

    return _create_indexing_job


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "job_status, details",
    [
        (JobStatus.FAILED, "text"),
        (JobStatus.PENDING, None),
        (JobStatus.RUNNING, "text"),
        (JobStatus.SUCCESS, None)
    ]
)
async def test_create_job_success(job_factory, job_status, details):
    """Test that Job is created."""
    repository_ids = [uuid4()]
    created_job = await job_factory(
        status=job_status,
        repository_ids=repository_ids,
        details=details
    )

    assert created_job.id is not None
    assert created_job.repository_ids == repository_ids
    assert created_job.status == job_status
    assert created_job.details == details
    assert created_job.status == job_status
    assert created_job.created_at is not None


@pytest.mark.asyncio
async def test_delete_job_success(job_repo, job_factory):
    """Test that Job is deleted."""
    created_job = await job_factory(
        repository_ids=[uuid4()]
    )

    delete_status = await job_repo.delete_job(created_job.id)

    assert delete_status

    job_from_db = await job_repo.get_job(created_job.id)

    assert job_from_db is None


@pytest.mark.asyncio
async def test_delete_job_not_found(job_repo):
    """Test that Job is not deleted when it doesn't exist."""
    delete_status = await job_repo.delete_job(uuid4())

    assert not delete_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "job_status, details",
    [
        (JobStatus.FAILED, "text"),
        (JobStatus.PENDING, None),
        (JobStatus.RUNNING, "text"),
        (JobStatus.SUCCESS, None)
    ]
)
async def test_get_job_success(job_repo, job_factory, job_status, details):
    """Test that Job is extracted by its id."""
    created_job = await job_factory(
        repository_ids=[uuid4()],
        status=job_status,
        details=details
    )

    job_from_db = await job_repo.get_job(created_job.id)

    assert job_from_db == created_job


@pytest.mark.asyncio
async def test_get_job_not_found(job_repo):
    """Test that Job is not extracted when it doesn't exist."""
    job_from_db = await job_repo.get_job(uuid4())

    assert job_from_db is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_job_status, new_job_status",
    [
        (JobStatus.FAILED, JobStatus.PENDING),
        (JobStatus.PENDING, JobStatus.RUNNING),
        (JobStatus.RUNNING, JobStatus.SUCCESS),
        (JobStatus.SUCCESS, JobStatus.FAILED)
    ]
)
async def test_update_job_status_success(job_repo, job_factory, old_job_status, new_job_status):
    """Test that Job's status is updated."""
    created_job = await job_factory(
        repository_ids=[uuid4()],
        status=old_job_status,
    )

    updated_job = await job_repo.update_job_status(
        job_id=created_job.id,
        new_status=new_job_status
    )

    assert updated_job.status == new_job_status
    assert updated_job.id == created_job.id
    assert updated_job.created_at == created_job.created_at
    if new_job_status in [JobStatus.FAILED, JobStatus.SUCCESS]:
        assert updated_job.finished_at is not None
    else:
        assert updated_job.finished_at is None


    updated_job_from_db = await job_repo.get_job(created_job.id)

    assert updated_job_from_db == updated_job


@pytest.mark.asyncio
async def test_update_job_status_not_found(job_repo):
    """Test that Job's status is not updated when it doesn't exist."""
    updated_job = await job_repo.update_job_status(
        job_id=uuid4(),
        new_status=JobStatus.FAILED
    )

    assert updated_job is None

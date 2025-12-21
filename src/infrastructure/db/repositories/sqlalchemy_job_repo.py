from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.knowledge import IndexingJob as DomainIndexingJob, JobStatus
from src.domain.repositories.job_repo import IJobRepository
from src.infrastructure.db.models.job import IndexingJob as ORMIndexingJob


class SqlAlchemyJobRepository(IJobRepository):

    """Job's repository realisation for SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(
            self,
            job_id: str,
            repo_ids: List[int],
            status: JobStatus,
            details: str
    ) -> DomainIndexingJob:
        """Create an indexing job."""
        clean_repo_ids = [str(item) for item in repo_ids]
        clean_job_id = str(job_id)

        job = ORMIndexingJob(
            id=clean_job_id,
            repository_ids=clean_repo_ids,
            status=status,
            details=details
        )

        self.session.add(job)
        await self.session.flush()
        return DomainIndexingJob.model_validate(job)

    async def delete_job(self, job_id: str) -> bool:
        """Delete an existing job by its id.

        Return true if deleted, false if the job doesn't exist.
        """
        stmt = select(ORMIndexingJob).where(ORMIndexingJob.id == job_id)
        result = await self.session.execute(stmt)
        orm_job = result.scalar_one_or_none()

        if not orm_job:
            return False

        await self.session.delete(orm_job)
        await self.session.flush()

        return True

    async def get_job(self, job_id: str) -> Optional[DomainIndexingJob]:
        """Get an indexing job by its id."""
        stmt = select(ORMIndexingJob).where(ORMIndexingJob.id == job_id)
        result = await self.session.execute(stmt)
        orm_job = result.scalar_one_or_none()
        if orm_job:
            return DomainIndexingJob.model_validate(orm_job)

        return None

    async def update_job_status(
            self,
            job_id: str,
            new_status: JobStatus
    ) -> Optional[DomainIndexingJob]:
        """Update a status of an existing job by its id."""
        stmt = select(ORMIndexingJob).where(ORMIndexingJob.id == job_id)
        result = await self.session.execute(stmt)
        orm_job = result.scalar_one_or_none()

        if not orm_job:
            return None

        orm_job.status = new_status.value
        if new_status in [JobStatus.FAILED, JobStatus.SUCCESS]:
            orm_job.finished_at = datetime.now()

        await self.session.flush()
        await self.session.refresh(orm_job)

        return DomainIndexingJob.model_validate(orm_job)

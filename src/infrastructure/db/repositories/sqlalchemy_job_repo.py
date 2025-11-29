from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.job_repo import IJobRepository
from src.infrastructure.db.models.job import IndexingJob


class SqlAlchemyJobRepository(IJobRepository):

    """Job's repository realisation for SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(
            self,
            job_id: str,
            repo_ids: List[int],
            status: str,
            details: str
    ) -> IndexingJob:
        """Create an indexing job."""
        clean_repo_ids = [str(item) for item in repo_ids]
        clean_job_id = str(job_id)

        job = IndexingJob(
            id=clean_job_id,
            repository_ids=clean_repo_ids,
            status=status,
            details=details
        )

        self.session.add(job)
        await self.session.flush()
        return job

    async def get_job(self, job_id: str) -> Optional[IndexingJob]:
        """Get an indexing job by its id."""
        stmt = select(IndexingJob).where(IndexingJob.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

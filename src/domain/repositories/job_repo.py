from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.knowledge import IndexingJob, JobStatus


class IJobRepository(ABC):

    """Class sets the contract by which Application-layer connects with Infrastructure-layer."""

    @abstractmethod
    async def create_job(
        self,
        job_id: UUID,
        repo_ids: List[UUID],
        status: JobStatus,
        details: str
    ) -> IndexingJob:
        """Create an indexing job."""
        raise NotImplementedError

    @abstractmethod
    async def delete_job(self, job_id: UUID) -> bool:
        """Delete an existing job by its id.

        Return true if deleted, false if the job doesn't exist.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_job(self, job_id: UUID) -> Optional[IndexingJob]:
        """Get an indexing job by its id."""
        raise NotImplementedError

    @abstractmethod
    async def update_job_status(
        self,
        job_id: UUID,
        new_status: JobStatus
    ) -> Optional[IndexingJob]:
        """Update a status of an existing job by its id."""
        raise NotImplementedError

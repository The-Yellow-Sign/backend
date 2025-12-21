from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.knowledge import JobStatus
from src.infrastructure.db.models.job import IndexingJob


class IJobRepository(ABC):

    """Class sets the contract by which Application-layer connects with Infrastructure-layer."""

    @abstractmethod
    async def create_job(
        self,
        job_id: str,
        repo_ids: List[int],
        status: JobStatus,
        details: str
    ) -> IndexingJob:
        """Create an indexing job."""
        raise NotImplementedError

    @abstractmethod
    async def delete_job(self, job_id: str) -> bool:
        """Delete an existing job by its id.

        Return true if deleted, false if the job doesn't exist.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_job(self, job_id: str) -> Optional[IndexingJob]:
        """Get an indexing job by its id."""
        raise NotImplementedError

    @abstractmethod
    async def update_job_status(self, job_id: str, new_status: JobStatus) -> Optional[IndexingJob]:
        """Update a status of an existing job by its id."""
        raise NotImplementedError

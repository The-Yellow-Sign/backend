from abc import ABC, abstractmethod
from typing import List, Optional

from src.infrastructure.db.models.job import IndexingJob


class IJobRepository(ABC):

    """Class sets the contract by which Application-layer connects with Infrastructure-layer."""

    @abstractmethod
    async def create_job(
        self,
        job_id: str,
        repo_ids: List[int],
        status: str,
        details: str
    ) -> IndexingJob:
        """Create an indexing job."""
        raise NotImplementedError

    @abstractmethod
    async def get_job(self, job_id: str) -> Optional[IndexingJob]:
        """Get an indexing job by its id."""
        raise NotImplementedError

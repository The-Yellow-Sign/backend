import uuid
from datetime import datetime

from src.domain.models.knowledge import IndexingJob


class MLOpsClient:

    """MLOps client (yet just a mock)."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def trigger_indexing(
        self,
        repo_ids: list[uuid.UUID],
        gitlab_url: str,
        gitlab_token: str
    ) -> IndexingJob:
        """Make a request to start an indexing process."""
        return IndexingJob(
            id=uuid.uuid4(),
            status="RUNNING",
            repository_ids=repo_ids,
            created_at=datetime.now(),
            details=f"Mock triggered for repos {repo_ids}"
        )

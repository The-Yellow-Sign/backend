import uuid
from datetime import datetime

from src.api.schemas.repository import IndexingJob


class MLOpsClient:

    """MLOps client (yet just a mock)."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def trigger_indexing(
        self,
        repo_ids: list[int],
        gitlab_url: str,
        gitlab_token: str
    ) -> IndexingJob:
        """Make a request to start an indexing process."""
        return IndexingJob(
            id=str(uuid.uuid4()),
            status="RUNNING",
            created_at=datetime.now(),
            details=f"Mock triggered for repos {repo_ids}"
        )

import uuid
from typing import List

from src.domain.models.knowledge import Repository


class GitLabClient:

    """GitLab client (yet just a mock)."""

    async def list_projects(self, base_url: str, token: str) -> List[Repository]:
        """Make a request and get all gitlab repositories."""
        return [
            Repository(
                id=str(uuid.uuid4()),
                name="Mock",
                path_with_namespace="iter1/mock",
                url="https://www.gitlab.com/mock_repo"
            )
        ]

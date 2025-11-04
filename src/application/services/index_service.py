from typing import List
from pydantic import HttpUrl, SecretStr
from datetime import datetime

from src.domain.models.knowledge import Repository, IndexingJob


class IndexService:
    async def update_gitlab_config(self, instance_url: HttpUrl, private_token: SecretStr):
        # сохранение урла к репе + токена
        return {"status": "ok", "message": "GitLab configuration updated."}

    async def get_gitlab_repositories(self) -> List[Repository]:
        return [
            Repository(
                id=1,
                name="Project Alpha",
                path_with_namespace="group-1/project-alpha",
                web_url="https://gitlab.example.com/group-1/project-alpha"
            ),
            Repository(
                id=2,
                name="Project Beta (Docs)",
                path_with_namespace="group-2/project-beta",
                web_url="https://gitlab.example.com/group-2/project-beta"
            )
        ]

    async def trigger_indexing(self, repository_ids: List[int]) -> IndexingJob:
        # дергает пайп с индексацией репозитория
        return IndexingJob(
            job_id="mock_job_id",
            status="PENDING",
            triggered_at=datetime.now(),
            details=f"Job submitted for repos: {repository_ids}"
        )
        
    async def get_indexing_status(self, job_id: str) -> IndexingJob:
        return IndexingJob(
            job_id=job_id,
            status="RUNNING",
            triggered_at=datetime.now() - datetime.timedelta(minutes=5),
            details="Step 2/5: Cloning repositories..."
        )

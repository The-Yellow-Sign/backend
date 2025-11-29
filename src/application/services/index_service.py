from typing import List, Optional

from fastapi import HTTPException, status

from src.api.schemas.repository import IndexingJob as IndexingJobSchema
from src.core.settings import settings
from src.domain.models.knowledge import Repository
from src.domain.repositories.gitlab_repo import IGitLabRepository
from src.domain.repositories.job_repo import IJobRepository
from src.infrastructure.external.gitlab_client import GitLabClient
from src.infrastructure.external.mlops_client import MLOpsClient
from src.infrastructure.security.encription import decrypt_data, encrypt_data


class IndexService:

    """Provides methods for GitLab indexing service."""

    def __init__(
            self,
            gitlab_repo: IGitLabRepository,
            job_repo: IJobRepository
    ):
            self.gitlab_repo = gitlab_repo
            self.job_repo = job_repo

            self.gitlab_client = GitLabClient()
            self.mlops_client = MLOpsClient(base_url=settings.MLOPS_SERVICE_URL.get_secret_value())

    async def configure_gitlab(self, url: str, private_token: str):
        """Set up url and token (by encripting the original one) for GitLab."""
        encrypted_token = encrypt_data(private_token)

        await self.gitlab_repo.save_config(url, encrypted_token)

        return {"status": "ok", "message": "GitLab configuration saved successfully."}

    async def list_repositories(self) -> List[Repository]:
        """Get all repositories for given GitLab instance."""
        config = await self.gitlab_repo.get_config()
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitLab is not configured yet. Please add config first."
            )

        raw_token = decrypt_data(config.private_token_encrypted)

        return await self.gitlab_client.list_projects(
            base_url=config.url,
            token=raw_token
        )

    async def trigger_indexing(self, repository_ids: List[int]) -> IndexingJobSchema:
        """Trigger and run indexing service."""
        config = await self.gitlab_repo.get_config()
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitLab is not configured yet. You should configure it first."
            )

        decrypted_token = decrypt_data(config.private_token_encrypted)

        job_info = await self.mlops_client.trigger_indexing(
            repo_ids=repository_ids,
            gitlab_url=config.url,
            gitlab_token=decrypted_token
        )

        await self.job_repo.create_job(
            job_id=job_info.id,
            repo_ids=repository_ids,
            status=job_info.status,
            details=job_info.details
        )

        return job_info

    async def get_indexing_status(self, job_id: str) -> Optional[IndexingJobSchema]:
        """Get status for existing indexing job."""
        job = await self.job_repo.get_job(job_id)
        if not job:
            return None

        return IndexingJobSchema(
            id=job.id,
            status=job.status,
            triggered_at=job.created_at,
            details=job.details
        )

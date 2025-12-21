from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_current_admin_user
from src.api.schemas.repository import IndexingJob, RepoConfig, Repository, SyncRequest

router_repository = APIRouter(
    dependencies=[Depends(get_current_admin_user)]
)

@router_repository.post("/", status_code=status.HTTP_202_ACCEPTED)
async def configure_repo(config: RepoConfig):
    """Save repo's link and private token."""
    ...

@router_repository.get(
    "/list",
    response_model=List[Repository]
)
async def list_gitlab_repositories():
    """Get list of repositories that are available for indexing."""
    ...

@router_repository.post(
    "/trigger",
    response_model=IndexingJob
)
async def trigger_indexing(sync_request: SyncRequest):
    """Start an indexing of repositories by their ids."""
    return IndexingJob(
        job_id="12345",
        status="PENDING",
        triggered_at=datetime.now(),
        details="mlops джоба запущена"
    )

@router_repository.get(
    "/status/{job_id}",
    response_model=IndexingJob
)
async def get_indexing_status(job_id: str):
    """Get status of indexing job by its id."""
    ...

from typing import List

from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_current_admin_user, get_index_service
from src.api.schemas.repository import GitLabConfigCreate, IndexingJob, Repository, SyncRequest
from src.application.services.index_service import IndexService

router_repository = APIRouter(dependencies=[Depends(get_current_admin_user)])


@router_repository.post("/config", status_code=status.HTTP_202_ACCEPTED)
async def configure_gitlab(
    config_data: GitLabConfigCreate,
    service: IndexService = Depends(get_index_service)
):
    """Save GitLab instans' link and private token."""
    return await service.configure_gitlab(
        url=str(config_data.url),
        private_token=config_data.private_token
    )


@router_repository.get("/list", response_model=List[Repository])
async def list_gitlab_repositories(
    service: IndexService = Depends(get_index_service)
):
    """Get list of repositories that are available for indexing."""
    return await service.list_repositories()


@router_repository.post("/trigger", response_model=IndexingJob)
async def trigger_indexing(
    sync_request: SyncRequest,
    service: IndexService = Depends(get_index_service)
):
    """Start an indexing of repositories by their ids."""
    return await service.trigger_indexing(
        repository_ids=sync_request.repository_ids
    )


@router_repository.get("/status/{job_id}", response_model=IndexingJob)
async def get_indexing_status(
    job_id: str,
    service: IndexService = Depends(get_index_service)
):
    """Get status of indexing job by its id."""
    return await service.get_indexing_status(job_id)

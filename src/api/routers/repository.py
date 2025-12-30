from typing import List

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_admin_user
from src.api.schemas.repository import (
    GitLabConfigCreate,
    IndexingJob,
    JobStatusUpdate,
    Repository,
    SyncRequest,
)
from src.application.services.index_service import IndexService

router_repository = APIRouter(
    dependencies=[Depends(get_current_admin_user)],
    route_class=DishkaRoute
)


@router_repository.post("/config", status_code=status.HTTP_202_ACCEPTED)
async def configure_gitlab(
    config_data: GitLabConfigCreate,
    service: FromDishka[IndexService]
):
    """Save GitLab instans' link and private token."""
    return await service.configure_gitlab(
        url=str(config_data.url),
        private_token=config_data.private_token
    )


@router_repository.get("/list", response_model=List[Repository])
async def list_gitlab_repositories(
    service: FromDishka[IndexService]
):
    """Get list of repositories that are available for indexing."""
    return await service.list_repositories()


@router_repository.post("/trigger", response_model=IndexingJob)
async def trigger_indexing(
    sync_request: SyncRequest,
    service: FromDishka[IndexService]
):
    """Start an indexing of repositories by their ids."""
    return await service.trigger_indexing(
        repository_ids=sync_request.repository_ids
    )

@router_repository.delete("/{job_id}")
async def delete_indexing_job(
    job_id: str,
    service: FromDishka[IndexService]
):
    """Delete an existing job by its id.

    Return true if deleted, false if the job doesn't exist.
    """
    return await service.delete_indexind_job(job_id)

@router_repository.get("/status/{job_id}", response_model=IndexingJob)
async def get_indexing_status(
    job_id: str,
    service: FromDishka[IndexService]
):
    """Get status of indexing job by its id."""
    return await service.get_indexing_status(job_id)


@router_repository.put("/status/{job_id}", response_model=IndexingJob)
async def update_indexing_status(
    job_id: str,
    status_update: JobStatusUpdate,
    service: FromDishka[IndexService]
):
    """Update a status of an existing job by its id."""
    updated_job = await service.update_indexing_status(job_id, status_update)
    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )

    return updated_job

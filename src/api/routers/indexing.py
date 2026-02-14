
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import PermissionChecker
from src.api.schemas.repository import (
    IndexingJob,
    JobStatusUpdate,
    SyncRequest,
)
from src.application.services.index_service import IndexService
from src.core.security_policy import Action

router_indexing = APIRouter(
    route_class=DishkaRoute
)


@router_indexing.post(
    "/trigger",
    response_model=IndexingJob,
    dependencies=[Depends(PermissionChecker(Action.INDEXING_TRIGGER))]
)
async def trigger_indexing(
    sync_request: SyncRequest,
    service: FromDishka[IndexService]
):
    """Start an indexing of repositories by their ids."""
    return await service.trigger_indexing(
        repository_ids=sync_request.repository_ids
    )


@router_indexing.delete(
    "/{job_id}",
    dependencies=[Depends(PermissionChecker(Action.INDEXING_DELETE))]
)
async def delete_indexing_job(
    job_id: str,
    service: FromDishka[IndexService]
):
    """Delete an existing job by its id.

    Return true if deleted, false if the job doesn't exist.
    """
    return await service.delete_indexind_job(job_id)


@router_indexing.get(
    "/status/{job_id}",
    response_model=IndexingJob,
    dependencies=[Depends(PermissionChecker(Action.INDEXING_GET))]
)
async def get_indexing_status(
    job_id: str,
    service: FromDishka[IndexService]
):
    """Get status of indexing job by its id."""
    return await service.get_indexing_status(job_id)


@router_indexing.put(
    "/status/{job_id}",
    response_model=IndexingJob,
    dependencies=[Depends(PermissionChecker(Action.INDEXING_UPDATE))]
)
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

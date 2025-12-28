
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_admin_user, get_index_service
from src.api.schemas.repository import (
    IndexingJob,
    JobStatusUpdate,
    SyncRequest,
)
from src.application.services.index_service import IndexService

router_indexing = APIRouter(dependencies=[Depends(get_current_admin_user)])


@router_indexing.post("/trigger", response_model=IndexingJob)
async def trigger_indexing(
    sync_request: SyncRequest,
    service: IndexService = Depends(get_index_service)
):
    """Start an indexing of repositories by their ids."""
    return await service.trigger_indexing(
        repository_ids=sync_request.repository_ids
    )


@router_indexing.delete("/{job_id}")
async def delete_indexing_job(
    job_id: str,
    service: IndexService = Depends(get_index_service)
):
    """Delete an existing job by its id.

    Return true if deleted, false if the job doesn't exist.
    """
    return await service.delete_indexind_job(job_id)


@router_indexing.get("/status/{job_id}", response_model=IndexingJob)
async def get_indexing_status(
    job_id: str,
    service: IndexService = Depends(get_index_service)
):
    """Get status of indexing job by its id."""
    return await service.get_indexing_status(job_id)


@router_indexing.put("/status/{job_id}", response_model=IndexingJob)
async def update_indexing_status(
    job_id: str,
    status_update: JobStatusUpdate,
    service: IndexService = Depends(get_index_service)
):
    """Update a status of an existing job by its id."""
    updated_job = await service.update_indexing_status(job_id, status_update)
    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )

    return updated_job

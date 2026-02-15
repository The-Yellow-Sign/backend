from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from src.domain.models.knowledge import JobStatus


class GitLabConfigCreate(BaseModel):

    """Data structure for GitLab config create schema."""

    url: HttpUrl
    private_token: str


class Repository(BaseModel):

    """Data structure for repository."""

    id: UUID
    name: str
    path_with_namespace: str = Field(..., example="group/my-awesome-project")
    url: HttpUrl


class SyncRequest(BaseModel):  # разделить на два разных типа - одиночный и multi?

    """Data strucuture for repositories indexing request."""

    repository_ids: List[UUID]


class IndexingJob(BaseModel):

    """Data structure for an existing indexing job."""

    id: UUID
    status: JobStatus
    repository_ids: List[UUID]
    created_at: datetime
    finished_at: Optional[datetime] = None
    details: Optional[str] = None  # возможно мета инфа


class JobStatusUpdate(BaseModel):

    """Data structure for job's status updating."""

    status: JobStatus = Field(..., description="New job's status")

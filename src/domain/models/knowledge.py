from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class JobStatus(str, Enum):

    """Data structure for job status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class GitLabConfig(BaseModel):

    """Data structure for GitLab config model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    url: HttpUrl
    private_token_encrypted: str


class Repository(BaseModel):

    """Data structure for repository."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    path_with_namespace: str
    url: HttpUrl


class IndexingJob(BaseModel):

    """Data structure for an existing indexing job."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: JobStatus
    repository_ids: List[UUID]
    created_at: datetime
    finished_at: Optional[datetime] = None
    details: Optional[str] = None

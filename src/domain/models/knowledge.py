from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID


class JobStatus(str, Enum):

    """Data structure for job status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass
class GitLabConfig:

    """Data structure for GitLab config model."""

    id: int
    url: str
    private_token_encrypted: str


@dataclass
class Repository:

    """Data structure for repository."""

    id: UUID
    name: str
    path_with_namespace: str
    web_url: str


@dataclass
class IndexingJob:

    """Data structure for an existing indexing job."""

    id: UUID
    status: JobStatus
    repository_ids: List[UUID]
    created_at: datetime
    finished_at: Optional[datetime] = None
    details: Optional[str] = None

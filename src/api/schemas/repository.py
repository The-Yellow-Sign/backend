from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, HttpUrl


class GitLabConfigCreate(BaseModel):

    """Data structure for GitLab config create schema."""

    url: str = Field(...)
    private_token: str = Field(...)


class Repository(BaseModel):

    """Data structure for repository."""

    id: UUID4
    name: str = Field(...)
    path_with_namespace: str = Field(..., example="group/my-awesome-project")
    web_url: HttpUrl


class SyncRequest(BaseModel):  # разделить на два разных типа - одиночный и multi?

    """Data strucuture for repositories indexing request."""

    repository_ids: List[UUID4] = Field(...)


class IndexingJob(BaseModel):

    """Data structure for an existing indexing job."""

    id: UUID4
    status: str = Field(..., example="RUNNING")
    triggered_at: datetime
    details: Optional[str] = None  # возможно мета инфа

from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, HttpUrl, SecretStr


class RepoConfig(BaseModel):

    """Data structuture for repository connection settings."""

    instance_url: HttpUrl = Field(...)
    private_token: SecretStr = Field(...)


class Repository(BaseModel):

    """Data structure for repository."""

    id: UUID4
    name: str = Field(...)
    path_with_namespace: str = Field(..., example="group/my-awesome-project")
    web_url: HttpUrl


class SyncRequest(BaseModel): # разделить на два разных типа - одиночный и multi?

    """Data strucuture for repositories indexing request."""

    repository_ids: List[UUID4] = Field(...)


class IndexingJob(BaseModel):

    """Data structure for an existing indexing job."""

    job_id: str
    status: str = Field(..., example="RUNNING")
    triggered_at: datetime
    details: Optional[str] = None # возможно мета инфа

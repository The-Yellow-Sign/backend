from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, HttpUrl


class GitLabConfigModel(BaseModel):

    """Data structure for GitLab config model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str


class Repository(BaseModel):

    """Data structure for repository."""

    id: UUID4
    name: str
    path_with_namespace: str
    web_url: HttpUrl


class IndexingJob(BaseModel):

    """Data structure for an existing indexing job."""

    id: str
    status: str
    triggered_at: datetime
    finished_at: Optional[datetime] = None
    details: Optional[str] = None

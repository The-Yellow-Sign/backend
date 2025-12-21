from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class Repository(BaseModel):

    """Data structure for repository."""

    id: int
    name: str
    path_with_namespace: str
    web_url: HttpUrl


class IndexingJob(BaseModel):

    """Data structure for an existing indexing job."""

    job_id: str
    status: str
    triggered_at: datetime
    finished_at: Optional[datetime] = None
    details: Optional[str] = None

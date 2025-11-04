from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class Repository(BaseModel):
    id: int
    name: str
    path_with_namespace: str
    web_url: HttpUrl


class IndexingJob(BaseModel):
    job_id: str
    status: str
    triggered_at: datetime
    finished_at: Optional[datetime] = None
    details: Optional[str] = None

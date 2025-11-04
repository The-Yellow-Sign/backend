from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


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

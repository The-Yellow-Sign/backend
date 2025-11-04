from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, HttpUrl, SecretStr


class RepoConfig(BaseModel):
    instance_url: HttpUrl = Field(...)
    private_token: SecretStr = Field(...)


class Repository(BaseModel):
    id: UUID4
    name: str = Field(...)
    path_with_namespace: str = Field(..., example="group/my-awesome-project")
    web_url: HttpUrl


class SyncRequest(BaseModel): # разделить на два разных типа - одиночный и multi?
    repository_ids: List[UUID4] = Field(...)


class IndexingJob(BaseModel):
    job_id: str
    status: str = Field(..., example="RUNNING")
    triggered_at: datetime
    details: Optional[str] = None # возможно мета инфа

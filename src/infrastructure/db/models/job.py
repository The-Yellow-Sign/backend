from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructure.db.models.base import Base


class IndexingJob(Base):

    """ORM-model for an indexing job."""

    __tablename__ = "indexing_jobs"

    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    repository_ids: Mapped[list] = mapped_column(JSON, nullable=False)

    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"IndexingJob(id={self.id!r}, status={self.status!r})"

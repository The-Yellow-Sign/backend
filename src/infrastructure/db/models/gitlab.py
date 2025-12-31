from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models.base import Base


class GitLabConfig(Base):

    """ORM-model for GitLab connection settings."""

    __tablename__ = "gitlab_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    private_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"GitLabConfig(url={self.url!r})"

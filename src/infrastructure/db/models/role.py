from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.models import Base


class Role(Base):

    """ORM-model for roles table."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    permissions: Mapped[list] = mapped_column(JSON, default=[])

    def __repr__(self) -> str:
        return f"Role(name={self.name!r})"

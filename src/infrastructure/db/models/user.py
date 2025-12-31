from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.models.user import User as DomainUser
from src.infrastructure.db.models import Base


class User(Base):

    """ORM-model for users table."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, role={self.role!r})"

    def update_from_domain(self, domain_user: DomainUser) -> None:
        """Update fields by values from domain model."""
        self.username = domain_user.username
        self.email = domain_user.email
        self.role = domain_user.role
        self.hashed_password = domain_user.hashed_password

